from ambar_conversion import conversion

#para conversao de um usuario de santa barbara d'oeste
a = conversion('CPFL','SBO') #Indica a cidade a concessionaria
#Conta da Loraine de dezembro
#CPF:337.896.888-51
#Numero CPFL: 4001760642
#Valor da conta: 34,32

#Argumentos do metodo conversion
# Tipo de renda: 'normal' ou 'baixa'
# kWh consumidos
# kWh gerado
# dias de bandeira verde
# dias de bandeira amarela
# dias de bandeira vermelha
# tipo da entrada: 'monofasica','bifasica','trifasica'
print(a.conversion('normal',106,76,26,4,0,'monofasica'))

#Conta da Elisete de dezembro
#CPF:337.896.888-51
#Numero CPFL: 4001760642
#Valor da conta(sem multas de atraso): 51,73
print(a.conversion('baixa',179,83,26,4,0,'monofasica'))

