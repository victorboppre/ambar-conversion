'''
Created on 18 de jan de 2019

@author: Victor Oliveira Boppre
Modificado por : Larissa Aquino em 14 de fev de 2019
'''
from firebase import firebase
import numpy as np
class conversion:
    '''
    classdocs
    '''
    def __init__(self, concessionaria, cidade):
        self.fb = firebase.FirebaseApplication('https://ambar-conversion.firebaseio.com/', None)
        infos = self.fb.get('/'+concessionaria+'/piscofins', None)
        self.med_trib = sum(infos)/len(infos)
        self.te = self.fb.get('/'+concessionaria+'/tarifas/TE', None)
        self.tusd = self.fb.get('/'+concessionaria+'/tarifas/TUSD', None)
        self.tusd_b = self.fb.get('/'+concessionaria+'/tarifas/TUSD_B_>220', None)
        self.ip = self.fb.get('/Cidades/'+cidade+'/IP', None)
        self.st = self.fb.get('/'+concessionaria+'/tarifas/ST', None) # Subvencao tarifaria
        self.std = self.fb.get('/'+concessionaria+'/tarifas/STD', None) # Desconto da subvencao tarifaria
        self.taf = {}
        self.taf['TE_B_30'] = self.te * 0.35
        self.taf['TUSD_B_30'] = self.tusd_b * 0.35
        self.taf['TE_B_100'] = self.te * 0.6
        self.taf['TUSD_B_100'] = self.tusd_b * 0.6
        self.taf['TE_B_220'] = self.te * 0.9
        self.taf['TUSD_B_220'] = self.tusd_b * 0.9
        self.taf['TE_B_>220'] = self.te
        self.taf['TUSD_B_>220'] = self.tusd_b

    def projection( self, kwh_c, kwh_g, tarifa, B_verde, B_amarela, B_vermelha, entrada):
        avg_c = np.average(kwh_c)
        avg_g = np.average(kwh_g)
        proj = self.conversion('tarifa', avg_c, avg_g, B_verde, B_amarela, B_vermelha, entrada)

        return proj


    def conversion( self, renda, kwh_consumido, kwh_injetado, bverde, bamarela, bvermelha, entrada):
        value1 = self.conv(renda, kwh_consumido, kwh_injetado, bverde, bamarela, bvermelha)
        if entrada == 'monofasica' and (kwh_consumido < 30 or (value1 < self.conv(renda,30,0,bverde,bamarela,bvermelha))):
            return self.conv(renda,30,0,bverde,bamarela,bvermelha)
        elif entrada == 'bifasica' and (kwh_consumido < 50 or (value1 < self.conv(renda,50,0,bverde,bamarela,bvermelha))):
            return self.conv(renda,50,0,bverde,bamarela,bvermelha)
        elif entrada == 'trifasica' and (kwh_consumido < 100 or (value1 < self.conv(renda,100,0,bverde,bamarela,bvermelha))):
            return self.conv(renda,100,0,bverde,bamarela,bvermelha)
        return value1

    def conv(self, renda, kwh_consumido, kwh_injetado, bverde, bamarela, bvermelha):
        if kwh_consumido< 100:
            ICMS = 0
        elif kwh_consumido >= 100 and kwh_consumido < 200:
            ICMS = 12
        else:
            ICMS = 25
        tributos = (1- self.med_trib/100 - ICMS/100)
        if renda == 'normal':
            #print('Tributos =')
            #print(str(self.med_trib)+'\n')
            reais = kwh_consumido*(self.te+self.tusd)/tributos
            #print('kW.h =')
            #print(str(kwh_consumido*(self.te+self.tusd)/tributos)+'\n')
            reais += 0.01*kwh_consumido*bamarela/((bverde+bamarela+bvermelha)*tributos)
            #print('Bandeira Amarela =')
            #print(str(0.01*kwh_consumido*bamarela/((bverde+bamarela+bvermelha)*tributos))+'\n')
            reais += 0.05*kwh_consumido*bvermelha/((bverde+bamarela+bvermelha)*tributos)
            #print('Bandeira Vermelha =')
            #print(str(0.05*kwh_consumido*bvermelha/((bverde+bamarela+bvermelha)*tributos))+'\n')
            reais -= kwh_injetado*(self.te+self.tusd)
            #print('kW.h Injetado')
            #print(str(kwh_injetado*(self.te+self.tusd))+'\n')
            reais += self.ip
            return reais

        else:
            if kwh_consumido <= 30:
                reais = kwh_consumido*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])/tributos
                #print('Menor que 30...')
                #print('Valor consumido ate 30 kW.h = '+str(reais))
            elif kwh_consumido <= 100:
                #print('Menor que 100...')
                reais = 30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])/tributos
                #print('Valor consumido ate 30 kW.h = '+str(reais))
                reais += (kwh_consumido - 30)*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])/tributos
                #print('Valor restante = '+str((kwh_consumido - 30)*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])/tributos))
            elif kwh_consumido <= 220:
                #print('Menor que 220...')
                reais = 30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])/tributos
                #print('Valor consumido ate 30 kW.h = '+str(reais))
                #print('Valor consumido ate 100 kW.h = '+str(70*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])/tributos))
                reais += 70*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])/tributos
                reais += (kwh_consumido - 100)*(self.taf['TE_B_220'] + self.taf['TUSD_B_220'])/tributos
                #print('Valor restante = '+ str((kwh_consumido - 100)*(self.taf['TE_B_220'] + self.taf['TUSD_B_220'])/tributos))
            else:
                reais = 30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])/tributos
                reais += 70*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])/tributos
                reais += (120)*(self.taf['TE_B_220'] + self.taf['TUSD_B_220'])/tributos
                reais += (kwh_consumido - 220)*(self.taf['TE_B_>220'] + self.taf['TUSD_B_>220'])/tributos

            if kwh_injetado < 30:
                reais -= kwh_injetado*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])
                #print('Menor que 30...')
                #print('Valor injetado ate 30 kW.h = '+str(kwh_injetado*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])))
            elif kwh_injetado <= 100:
                #print('Menor que 100...')
                reais -= 30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])
                #print('Valor injetado ate 30 kW.h = '+str(30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])))
                reais -= (kwh_injetado - 30)*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])
                #print('Valor restante injetado = '+str((kwh_injetado - 30)*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])))
            elif kwh_injetado <= 220:
                #print('Menor que 220...')
                reais -= 30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])
                #print('Valor injetado ate 30 kW.h = '+str(30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])))
                #print('Valor injetado ate 100 kW.h = '+str(70*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])))
                reais -= 70*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])
                reais -= (kwh_injetado - 100)*(self.taf['TE_B_220'] + self.taf['TUSD_B_220'])
                #print('Valor restante = '+ str(((kwh_injetado - 100)*(self.taf['TE_B_220'] + self.taf['TUSD_B_220'])))
            else:
                reais -= 30*(self.taf['TE_B_30'] + self.taf['TUSD_B_30'])
                reais -= 70*(self.taf['TE_B_100'] + self.taf['TUSD_B_100'])
                reais -= 120*(self.taf['TE_B_220'] + self.taf['TUSD_B_220'])
                reais -= (kwh_injetado - 220)*(self.taf['TE_B_>220'] + self.taf['TUSD_B_>220'])

            reais += (self.st-self.std)# Ha um desconto de subvencao tarifaria para usuarios de baixa renda, esse valor muda a cada mes. Pode ser encontrada na conta de luz.

            return reais
