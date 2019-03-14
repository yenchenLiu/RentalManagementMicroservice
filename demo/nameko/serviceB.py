from nameko.rpc import rpc, RpcProxy


class ServiceB:
    name = 'serviceB'

    @rpc
    def get_data(self):
        return "It's from ServiceB"
