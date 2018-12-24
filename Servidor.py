import cpuinfo
import psutil
import socket
import pickle
import os

udp_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_servidor.bind((socket.gethostname(), 9999))


info = cpuinfo.get_cpu_info()
disco = psutil.disk_usage('.')
total = round(disco.total/(1024**3), 2)
dic_interfaces = psutil.net_if_addrs()


def main():
    try:
        print(psutil.cpu_percent(percpu=True))
        print("Ouvindo a porta", 9999)

        while True:

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "cpu":
                info_cpu = exibe_info_cpu()
                p_bytes = pickle.dumps(info_cpu)
                udp_servidor.sendto(p_bytes, cliente)

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "memoria":
                info_memoria = exibe_uso_memoria()
                p_bytes = pickle.dumps(info_memoria)
                udp_servidor.sendto(p_bytes, cliente)

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "hd":
                info_hd = exibe_uso_disco()
                p_bytes = pickle.dumps(info_hd)
                udp_servidor.sendto(p_bytes, cliente)

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "cpu":
                info_cpu = exibe_uso_cpu()
                p_bytes = pickle.dumps(info_cpu)
                udp_servidor.sendto(p_bytes, cliente)

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "pids":
                info_pids = processos()
                p_bytes = pickle.dumps(info_pids)
                udp_servidor.sendto(p_bytes, cliente)

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "arquivos":
                info_arquivos = arquivos()
                p_bytes = pickle.dumps(info_arquivos)
                udp_servidor.sendto(p_bytes, cliente)

            (msg, cliente) = udp_servidor.recvfrom(1024)
            if msg.decode() == "rede":
                info_net = info_rede()
                p_bytes = pickle.dumps(info_net)
                udp_servidor.sendto(p_bytes, cliente)

            print('Enviado mensagem para o cliente!')
            print('Aguardando nova consulta!')

    except Exception as error:
        print(error)

    udp_servidor.close()


def exibe_info_cpu():

    system_os = os.path.basename('name')
    interfaces = psutil.net_if_addrs()

    if system_os == 'nt' or system_os == 'java':
        try:
            nome_interface = interfaces['eth0'][0].address  # para rede cabeada
        except Exception as error:
            nome_interface = str("Nenhuma interface de rede localizada: ") + str(error)
    else:
        try:
            nome_interface = interfaces['docker0'][0].address #quando tiver no wiffi pode colocar o wlan0
        except Exception as error:
            nome_interface = str("Nenhuma interface de rede localizada: ") + str(error)

    return (
        {"Nome": str(info["brand"])},
        {"Arquitetura": str(info["arch"])},
        {"Palavra (bits)": str(info["bits"])},
        {"Frequência (MHz)": str(round(psutil.cpu_freq().current, 2))},
        {"Núcleos (físicos)": str(psutil.cpu_count()) + "("+str(psutil.cpu_count(logical=False))+")"},
        {"IP": str(nome_interface)},
        {"Uso do disco": str(total)}
    )


def exibe_uso_memoria():
    return psutil.virtual_memory()


def exibe_uso_disco():
    return psutil.disk_usage('.')


def exibe_uso_cpu():
    return psutil.cpu_percent(percpu=True)


def processos():
    lista_proc = psutil.process_iter()
    percentual = 90
    soma = contador = 0
    lista = []
    lista_resp = []
    for p in lista_proc:
        try:
            pinfo = p.as_dict(attrs=['pid', 'name', 'memory_info'])
            nome = pinfo['name']
            mem = pinfo['memory_info']
            dic = {'PID': p.pid, 'Nome': nome, 'RSS': mem.rss, 'VMS': mem.vms}
            lista.append(dic)

            soma = soma + mem.rss
            contador = contador + 1
        except psutil.NoSuchProcess:
            pass
        media = soma / contador

    for i in lista:
        if i["RSS"] > (media + media * percentual / 100):
            lista_resp.append(i)
    return lista_resp


def arquivos():
    return os.listdir()


def info_rede():
    return psutil.net_if_addrs()


if __name__ == '__main__':
    main()