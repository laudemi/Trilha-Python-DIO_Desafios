# Desafio v.3
import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco) :
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)
    
    
 
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

    def __str__(self):
        return f"""\
        Titular:\t{self.nome}
        """
    
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s")
            }
        )

class Conta:
    def __init__(self, num, cliente):
        self._saldo = 0
        self._num = num
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, num, cliente):
        return cls(num, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def num(self):
        return self._num
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def sacar(self, valor):
        saldo = self.saldo
        saldo_excedido = valor > saldo

        if saldo_excedido:
            print("\n @@@ Operação falhou! VOcê não tem saldo suficiente! @@@")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso!! ===")
            return True
        
        else:
            print("\n @@@ Operação falhou! O valor informado não é válido! @@@")

        return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Deposito realizado com sucesso!! ===")
        else:
            print("\n @@@ Operação falhou! O valor informado não é válido! @@@")
            return False
        
        return True

class ContaCorrente(Conta):
        
    def __init__(self, num, cliente, limite=500, limite_saques=3):
        super().__init__(num, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        num_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        limite_excedido = valor > self._limite
        saques_excedidos = num_saques >= self._limite_saques
        
        if limite_excedido:
                print("\n @@@ Operação falho! Limite de saque excedido! @@@")

        elif saques_excedidos:
            print("\n @@@ Operação falho! Número máximo de saques excedido! @@@")
        else:
            return super().sacar(valor)
        
        return False

    def __str__(self):
        return f"""\
            Agência: \t{self.agencia}
            C/C:\t\t{self.num}
            Titular:\t{self.cliente.nome}
            """
    
class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """\n
    ================== MENU =====================
    [1] - Saque
    [2] - Depósito
    [3] - Extrato
    [4] - Novo Cliente
    [5] - Nova Conta
    [6] - Listar Contas
    [7] - Listar Clientes
    [0] - Sair
    ==============================================
    => """
    return input(textwrap.dedent(menu))

def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf] 
    return clientes_filtrados[0] if clientes_filtrados else None

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do Cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
  
    print("\n ================= Extrato ===================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações"
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo: \n\tR$ {conta.saldo:.2f}")
    print("================================================")

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n ### Cliente não possui conta! @@@")
        return
    
    # FIXME: Não permite cliente escolher a conta
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf,clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do Cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return
        
    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return
    
    cliente.realizar_transacao(conta, transacao)

def criar_clientes(clientes):
    cpf = input("Informe o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n @@@ Já existe cliente com esse CPF! @@@")
        return 
    
    nome = input("Informe o nome completo: ")
    data_nasc = input("Informe a data de nascimento (dd/mm/aaa): ")
    endereco = input("Informe o endereço (logradouro, numero, bairro, cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nasc, cpf=cpf, endereco=endereco)

    clientes.append(cliente)
    
    print("---------- Cliente cadastrado com sucesso!' ----------------")

def criar_conta(num_conta, clientes, contas):
    cpf = input("Informe o CPF do Cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n @@@ Cliente não encontrado, fluxo de criação de conta encerrado ! @@@")
        return
    
    conta = ContaCorrente.nova_conta(cliente=cliente, num=num_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n ==== Conta criada com sucesso! =====")
        
def listar_contas(contas):
    if contas == []:
        print("Nenhuma conta ativa!")
    else:
        for conta in contas:
            print("=" * 80)
            print(textwrap.dedent(str(conta)))

def listar_clientes(clientes):
    if clientes == []:
        print("Nenhum cliente existente!")
    else:  
        for cliente in clientes:
            print("=" * 80)
            print(textwrap.dedent(str(cliente))) 
                   

def main():
    clientes = []
    contas = []


    while True:
    
        opcao = menu()

        if opcao == "1":
            sacar(clientes)

        elif opcao == "2":
            depositar(clientes)
     
        elif opcao == "3":
            exibir_extrato(clientes)

        elif opcao == "4":
            criar_clientes(clientes)

        elif opcao == "5":
            num_conta = len(contas)+1
            criar_conta(num_conta, clientes, contas)
        
        elif opcao == "6":
            listar_contas(contas)

        elif opcao == "7":
            listar_clientes(clientes)

        elif opcao == "0":
            break

        else:
            print("Opção Inválida, por favor tente novamente...")

main()