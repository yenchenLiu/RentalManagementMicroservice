from nameko.standalone.rpc import ClusterRpcProxy


with ClusterRpcProxy({'AMQP_URI': "amqp://guest:guest@localhost"}) as rpc:
    print(rpc.serviceA.get_data())
    print(rpc.serviceA.get_data_from_serviceB())
