from nameko.rpc import rpc, RpcProxy


class ServiceA:
    name = 'serviceA'
    service_b = RpcProxy('serviceB')

    @rpc
    def get_data(self):
        return "It's from ServiceA"

    @rpc
    def get_data_from_serviceB(self):
        return self.service_b.get_data()
