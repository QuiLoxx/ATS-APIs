#!/usr/bin/env python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from distutils.version import LooseVersion
import logging
# ADDING for folks with newer versions of requets as urllib3 is no longer bundled with requets
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# REMOVE
from pprint import pprint as pp

logger = logging.getLogger(__name__)


class SCException(Exception):
	pass

class SCWarning(Warning):
	pass

class APIError(SCException):
	def __init__(self, http_status_code, error_code, error_msg):
		self.http_status_code = http_status_code
		self.error_code = error_code
		self.error_msg = error_msg.strip('\n')

	def __str__(self):
		msg = 'http_status_code[{}] error_code[{}]: {}'.format(self.http_status_code, self.error_code, self.error_msg)
		return msg
class PermissionsError(SCException):
	pass

class PermissionsWarning(SCWarning):
	pass

def ensureAdmin(func):
	def wrapper(*args, **kwargs):
		cls = args[0]
		if not cls.is_admin:
			msg = 'This function requires an administrator user.'
			raise PermissionsError(msg)
			cls.log.error(msg)
		return func(*args, **kwargs)
	return wrapper

def ensureNotAdmin(func):
	def wrapper(*args, **kwargs):
		cls = args[0]
		if cls.is_admin:
			msg = 'This function requires a non-administrator user.'
			raise PermissionsError(msg)
			cls.log.error(msg)
		return func(*args, **kwargs)
	return wrapper
def warnAdmin(func):
	def wrapper(*args, **kwargs):
		cls = args[0]
		if cls.is_admin:
			msg = 'Results may be incomplete since your user is a system admin.'
			raise PermissionsWarning(msg)
			cls.log.warn(msg)
		return func(*args, **kwargs)
	return wrapper

def warnNotAdmin(func):
	def wrapper(*args, **kwargs):
		msg = False
		cls = args[0]
		if not cls.is_admin:
			msg = 'Results may be incomplete since your user is not a system admin.'
			raise PermissionsWarning(msg)
			cls.log.warn(msg)
		return func(*args, **kwargs)
	return wrapper

class SecurityCenter(object):
	### Start Class Functions ###
	log_level = logging.WARNING
	page_size = 5000
	token = False
	least_supported_version = '5'

	def __init__(self, address, verify_ssl=False, protocol='https', port=443, auth_token=None, debug=False, **kwargs):
		self.log = logger
		self.debug = debug
		self.__setupLogging()
		self.verify_ssl = verify_ssl
		self.base_url = '{protocol}://{address}:{port}/rest/{{endpoint}}'.format(protocol=protocol,address=address,port=port)
		self.log.debug('Base URL: {}'.format(self.base_url))
		self.__setupSession()
		self.__checkServerVersion()

	def __setupSession(self):
		self.session = requests.Session()
		self.session.verify = self.verify_ssl
		if not self.verify_ssl:
			self.log.debug('Disabling InsecureRequestWarning since we arent verifying ssl certs.')
			requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
	def __checkServerVersion(self):
		data = self.getSystemInfo()
		version = data.get('version', '0.0.0')
		if LooseVersion(version) < LooseVersion(self.least_supported_version):
			msg = 'This version ({}) of SecurityCenter is not supported.'.format(version)
			self.log.error(msg)
			raise ValueError(msg)
		self.server_version = version

	def __createHandler(self):
		self.log.debug('Creating stream handler for script')
		handler = logging.StreamHandler()
		fmt = logging.Formatter('%(levelname)s: %(name)s: %(message)s')
		handler.setFormatter(fmt)
		handler.setLevel(self.log_level)
		return handler

	def __setupLogging(self):
		if self.debug:
			self.log_level = logging.DEBUG
			handler = self.__createHandler()
		else:
			handler = logging.NullHandler()
		self.log.setLevel(self.log_level)
		self.log.addHandler(handler)

	def __del__(self):
		self.log.debug('__del__ called')
		self.logout()

	def _setCurrentUser(self):
		self.log.debug('Setting current_user.')
		self.current_user = self._getCurrentUser()
		self._setIsAdmin()
		self.log.debug('Current User: {}'.format(self.current_user))


	def __checkResponse(self, response):
		self.log.debug('Checking response')
		data = response.json()
		error_code = data.get('error_code', 1)
		if error_code:
			self.log.error(response.url)
			raise APIError(response.status_code, error_code, data.get('error_msg', 'Unknown Error...'))
		elif 'releaseSession' in data['response']:
			raise APIError(response.status_code, error_code, 'There are no sessions available for this user. Please try .login(force_session=True)')

		return data['response']

	def login(self, username, password, force_session=False, **kwargs):
		self.log.debug('Logging in')
		endpoint = 'token'
		params = {
			'username': username,
			'password': password,
		}

		if force_session:
			params['releaseSession'] = force_session
			self.log.warn('An existing session for this user will be required to login again.')

		res = self.postEndpoint(endpoint, params)
		token = str(res['token'])
		self.token = token
		self.log.debug('Set token to: {}'.format(token))
		headers = {
			'Content-Type': 'application/json',
			'X-SecurityCenter': self.token,
		}
		self.session.headers.update(headers)
		self._setCurrentUser()

	def logout(self):
		if self.token:
			self.log.debug('Deleting current session (token).')
			endpoint = 'token'
			self.deleteEndpoint(endpoint)
			self.token = False

	### End Class Functions ###

	### Start API request Functions ###
	def __buildUrl(self, endpoint):
		return self.base_url.format(endpoint=endpoint.lstrip('/'))

	def postEndpoint(self, endpoint, params=None, json=None, data=None):
		url = self.__buildUrl(endpoint)
		self.log.debug('POST URL: {}'.format(url))
		self.log.debug('POST PARAMS: {}'.format(params))
		self.log.debug('POST JSON: {}'.format(json))
		r = self.session.post(url, params=params, json=json, data=data)
		return self.__checkResponse(r)

	def getEndpoint(self, endpoint, params=None):
		url = self.__buildUrl(endpoint)
		self.log.debug('GET URL: {}'.format(url))
		self.log.debug('GET PARAMS: {}'.format(params))
		r = self.session.get(url, params=params)
		return self.__checkResponse(r)

	def updateEndpoint(self, endpoint, params=None):
		url = self.__buildUrl(endpoint)
		self.log.debug('UPDATE URL: {}'.format(url))
		self.log.debug('UPDATE PARAMS: {}'.format(params))
		r = self.session.put(url, params=params)
		return self.__checkResponse(r)


	def deleteEndpoint(self, endpoint, params=None):
		url = self.__buildUrl(endpoint)
		self.log.debug('DELETE URL: {}'.format(url))
		self.log.debug('DELETE PARAMS: {}'.format(params))
		r = self.session.delete(url, params=params)
		return self.__checkResponse(r)

	### End API request Functions ###

	### Start plugin functions	###
	def _processXrefs(self, response):
		xrefs = response.get('xrefs', False)
		if xrefs and len(xrefs) > 0:
			items = xrefs.split(',')
			data = {}
			for i in items:
				t, v = i.strip().split(':')
				if t not in data:
					data[t] = list()
				data[t].append(v)
			response['xrefs'] = data
		return response
	def __pluginsToIdDict(self, response):
		ret = dict()
		for plugin_data in response:
			pid = plugin_data.pop('id')
			ret[pid] = plugin_data
		return ret

	def _getPlugins(self, plugin_type):
		endpoint = 'plugin'
		start_offset = 0
		end_offset = self.page_size
		ret = list()
		while True:
			params = {
				'startOffset': start_offset,
				'endOffset': end_offset,
				'type': plugin_type,
				'fields': 'id,name,description,family,type,copyright,version,sourceFile,dependencies,requiredPorts,requiredUDPPorts,cpe,srcPort,dstPort,protocol,riskFactor,solution,seeAlso,synopsis,checkType,exploitEase,exploitAvailable,exploitFrameworks,cvssVector,cvssVectorBF,baseScore,temporalScore,stigSeverity,pluginPubDate,pluginModDate,patchPubDate,patchModDate,vulnPubDate,modifiedTime,md5,xrefs',
			}
			res = self.getEndpoint(endpoint, params=params)
			ret.extend(res)
			if len(res) < self.page_size:
				break
			start_offset = end_offset
			end_offset = end_offset + self.page_size
		return ret


	def listPluginFamilies(self):
		endpoint = 'pluginFamily'
		params = {
			'fields': 'id,name,type',
			'type': 'all',
			'startOffset': 0,
			'endOffset': self.page_size,
		}
		return self.getEndpoint(endpoint, params=params)

	def getAllPlugins(self):
		plugin_type = 'all'
		return self._getPlugins(plugin_type)

	def getActivePlugins(self):
		plugin_type = 'active'
		return self._getPlugins(plugin_type)

	def getCompliancePlugins(self):
		plugin_type = 'compliance'
		return self._getPlugins(plugin_type)

	def getCustomPlugins(self):
		plugin_type = 'custom'
		return self._getPlugins(plugin_type)

	def getLcePlugins(self):
		plugin_type = 'lce'
		return self._getPlugins(plugin_type)

	def getNotPassivePlugins(self):
		plugin_type = 'notPassive'
		return self._getPlugins(plugin_type)

	def getPassivePlugins(self):
		plugin_type = 'passive'
		return self._getPlugins(plugin_type)

	def getPlugin(self, plugin_id):
		endpoint = 'plugin/{}'.format(plugin_id)
		params = {
			'fields': 'family,type,copyright,version,sourceFile,dependencies,requiredPorts,requiredUDPPorts,cpe,srcPort,dstPort,protocol,riskFactor,solution,seeAlso,synopsis,checkType,exploitEase,exploitAvailable,exploitFrameworks,cvssVector,cvssVectorBF,baseScore,temporalScore,stigSeverity,pluginPubDate,pluginModDate,patchPubDate,patchModDate,vulnPubDate,modifiedTime,md5,xrefs',
		}
		ret = self.getEndpoint(endpoint, params=params)
		return self._processXrefs(ret)
	###  End plugin functions	###

	### Start Analysis functions ###
	@ensureNotAdmin
	def getVulnAnalysis(self, query, source_type, sort_direction=None, sort_field=None):
		analysis_type = 'vuln'
		source_type = source_type.lower()
		if source_type not in ['individual', 'cumulative']:
			raise ValueError('[{}] is not supported for vuln analysis source_type. Only individual and cumulative are supported.'.format(source_type))
		params = {
			'type': analysis_type,
			'query': query,
			'sortDir': sort_direction,
			'sortField': sort_field,
			'sourceType': source_type,
		}
		return self.getAnalysis(**params)


	@ensureNotAdmin
	def getAnalysis(self, type, query, sourceType, sortDir=None, sortField=None, additional_params={}, **kwargs):
		endpoint = 'analysis'
		if not isinstance(query, dict):
			raise TypeError('query parameter must be a dictionary')
		base_params = {
			'type': type,
			'query': query,
			'sourceType': sourceType,
			"sortField":"score",
			"sortDir":"desc",
			'startOffset': 0,
			'endOffset': 1,
			"columns":[],
		}
		if not all((sortDir, sortField)):
			self.log.warn('sort_direction and sort_field must both be specified.')
			self.log.warn('Will not use specified sort_direction[{}] or sort_field[{}]'.format(sortDir,sortField))
		else:
			base_params['sortField'] = sortField
			base_params['sortDir'] = sortDir
		#add any special params passed for a given analysis, but dont overwrite anything we already set.
		for key in kwargs:
			if key not in params:
				base_params[key] = kwargs[key]
				self.log.debug('Adding param[{}] with value[{}] to analysis parameters.'.format(key, kwargs[key]))
		if not isinstance(additional_params, dict):
			raise TypeError('additional_params must be a dictionary')
		all_params = additional_params
		all_params.update(base_params)
		return self.postEndpoint(endpoint, json=all_params)

	### End Analysis functions ###

	### Start user functions    ###
	def getCurrentUser(self):
		return self.current_user

	def _getCurrentUser(self):
		endpoint = 'currentUser'
		params = {
			'fields': 'username,firstname,,lastname,status,role,title,email,address,city,state,country,phone,fax,createdTime,modifiedTime,lastLogin,lastLoginIP,mustChangePassword,locked,failedLogins,authType,fingerprint,password,description,managedUsersGroups,managedObjectsGroups,preferences,orgName ,responsibleAsset,group',
		}

		return self.getEndpoint(endpoint, params=params)

	def _setIsAdmin(self):
		self.log.debug('Determining if we are an admin.')
		if int(self.current_user['role']['id']) == 1:
			self.log.debug('Logged in as an admin.')
			self.is_admin = True
		else:
			self.is_admin = False
			self.log.debug('Logged in as normal user.')

	def isAdmin(self):
		return self.is_admin

	def whoAmI(self):
		ret = {
			'firstname': self.current_user['firstname'],
			'lastname': self.current_user['lastname'],
			'username': self.current_user['username'],
			'isAdmin': self.is_admin,
		}
		return ret
	### End user functions        ###

	### Start Scan Results functions   ###
	def listScanResults(self,fields=None):
		endpoint = 'scanResult'
		if fields is None:
			fields = 'id,name,description,status,initiator,owner,ownerGroup,repository,scan,job,details,importStatus,importStart,importFinish,importDuration?downloadAvailable,downloadFormat,dataFormat,resultType,resultSource,running,errorDetails,importErrorDetails,totalIPs,scannedIPs,startTime,finishTime,scanDuration?completedIPs,completedChecks,totalChecks'
		params = {
			'fields': fields,
		}
		return self.getEndpoint(endpoint, params=params)

	def getScanResult(self, id, fields=None):
		endpoint = 'scanResult/{}'.format(id)
		if fields is None:
			fields = 'id,name,description,status,progress,initiator,owner,ownerGroup,repository,scan,job,details,importStatus,importStart,importFinish,importDuration?downloadAvailable,downloadFormat,dataFormat,resultType,resultSource,running,errorDetails,importErrorDetails,totalIPs,scannedIPs,startTime,finishTime,scanDuration?completedIPs,completedChecks,totalChecks'
		params = {
			'fields': fields,
		}
		return self.getEndpoint(endpoint, params=params)

	### End Scan Results functions   ###

	### Start Scanenr functions   ###
	@warnNotAdmin
	def getScanners(self):
		endpoint = 'scanner'
		params = {
			'fields': 'ip,port,useProxy,enabled,verifyHost,managePlugins,authType,cert,username,password,agentCapable,version,webVersion,admin,msp,numScans,numHosts,numSessions,numTCPSessions,loadAvg,uptime,pluginSet,loadedPluginSet,serverUUID,createdTime,modifiedTime,zones,nessusManagerOrgs'
		}
		return self.getEndpoint(endpoint, params=params)

	@warnNotAdmin
	def getScanner(self, scanner_id):
		endpoint = 'scanner/{}'.format(scanner_id)
		params = {
			'fields': 'ip,port,useProxy,enabled,verifyHost,managePlugins,authType,cert,username,password,agentCapable,version,webVersion,admin,msp,numScans,numHosts,numSessions,numTCPSessions,loadAvg,uptime,pluginSet,loadedPluginSet,serverUUID,createdTime,modifiedTime,zones,nessusManagerOrgs',
		}
		return self.getEndpoint(endpoint, params=params)
	### End Scanner functions     ###

	### Start Query functions ###
	@ensureNotAdmin
	def listQueries(self, query_type='all', fields=None):
		endpoint = 'query'

		if not isinstance(fields, str):
			self.log.error('fields must be a comma-seperated string of fields to include.')
			self.log.warn('default fields will be used')
			fields = None
		if fields is None:
			fields = 'name,description,type'

		params = {
			'fields': fields,
			#'type': query_type,
		}
		return self.getEndpoint(endpoint, params=params)

	@ensureNotAdmin
	def getQueryDetails(self, query_id, fields=None):
		endpoint = '/query/{}'.format(query_id)
		if fields is None:
			fields = 'name,description,creator,owner,ownerGroup,targetGroup,tool,type,tags,context,browseColumns,browseSortColumn,browseSortDirection,createdTime,modifiedTime,status,filters,canManage,canUse,groups'
		params = {
			'fields': fields,
		}
		return self.getEndpoint(endpoint, params=params)

	### End Query functions ###
	### Start System functions ###
	def getSystemInfo(self):
		endpoint = '/system'
		return self.getEndpoint(endpoint)
	### End System functions ###
