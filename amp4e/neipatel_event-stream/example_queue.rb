require 'bunny'

connection_url = "#{amqp_credentials['proto']}://#{amqp_credentials['user_name']}:#{amqp_credentials['password']}@#{amqp_credentials['host']}:#{amqp_credentials['port']}"

conn = Bunny.new(connection_url)
conn.start

ch = conn.create_channel
q  = ch.queue(amqp_credentials['queue_name'], :passive => true, :durable => true)
x  = ch.default_exchange

q.subscribe(:block => true) do |delivery_info, metadata, payload|
  puts "Received #{payload}"
end
