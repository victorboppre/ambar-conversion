def projection( self, kwh_c, kwh_g, tarifa, B_verde, B_amarela, B_vermelha, entrada):
    avg_c = np.average(kwh_c)
    avg_g = np.average(kwh_g)
    proj = self.conversion('tarifa', avg_c, avg_g, B_verde, B_amarela, B_vermelha, entrada)

    return proj