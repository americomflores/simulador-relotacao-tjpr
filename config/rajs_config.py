"""
Configuração das Regiões Administrativas Judiciárias (RAJs) do TJPR.

As 10 RAJs organizam geograficamente as comarcas do Paraná para fins
administrativos do Tribunal de Justiça.
"""

RAJS = {
    "RAJ 1 - Região Metropolitana de Curitiba e Litoral": {
        "numero": 1,
        "sede": "Curitiba",
        "comarcas": [
            "Curitiba", "Almirante Tamandaré", "Antonina", "Araucária", "Bocaiúva do Sul",
            "Campina Grande do Sul", "Campo Largo", "Cerro Azul", "Colombo", "Fazenda Rio Grande",
            "Guaratuba", "Matinhos", "Morretes", "Paranaguá", "Pinhais", "Piraquara",
            "Pontal do Paraná", "Quatro Barras", "Rio Branco do Sul", "São José dos Pinhais"
        ]
    },
    "RAJ 2 - Ponta Grossa": {
        "numero": 2,
        "sede": "Ponta Grossa",
        "comarcas": [
            "Ponta Grossa", "Imbituva", "Ipiranga", "Jaguariaíva", "Mallet", "Palmeira",
            "Piraí do Sul", "Rebouças", "Reserva", "São João do Triunfo", "Sengés",
            "Teixeira Soares", "Tibagi", "Castro", "Irati", "Lapa", "Rio Negro",
            "São Mateus do Sul", "Telêmaco Borba", "União da Vitória"
        ]
    },
    "RAJ 3 - Guarapuava": {
        "numero": 3,
        "sede": "Guarapuava",
        "comarcas": [
            "Guarapuava", "Cândido de Abreu", "Cantagalo", "Iretama", "Manoel Ribas",
            "Palmital", "Pinhão", "Prudentópolis", "Ivaiporã", "Laranjeiras do Sul", "Pitanga"
        ]
    },
    "RAJ 4 - Francisco Beltrão": {
        "numero": 4,
        "sede": "Francisco Beltrão",
        "comarcas": [
            "Francisco Beltrão", "Ampére", "Barracão", "Clevelândia", "Coronel Vivida",
            "Marmeleiro", "Mangueirinha", "Realeza", "Salto do Lontra", "São João",
            "Chopinzinho", "Dois Vizinhos", "Palmas", "Pato Branco", "Santo Antônio do Sudoeste"
        ]
    },
    "RAJ 5 - Foz do Iguaçu": {
        "numero": 5,
        "sede": "Foz do Iguaçu",
        "comarcas": [
            "Foz do Iguaçu", "Matelândia", "Santa Helena", "São Miguel do Iguaçu", "Medianeira"
        ]
    },
    "RAJ 6 - Cascavel": {
        "numero": 6,
        "sede": "Cascavel",
        "comarcas": [
            "Cascavel", "Assis Chateaubriand", "Campina da Lagoa", "Capanema",
            "Capitão Leônidas Marques", "Catanduvas", "Corbélia", "Formosa do Oeste",
            "Guaraniaçu", "Mamborê", "Marechal Cândido Rondon", "Nova Aurora",
            "Palotina", "Quedas do Iguaçu", "Toledo", "Ubiratã"
        ]
    },
    "RAJ 7 - Umuarama": {
        "numero": 7,
        "sede": "Umuarama",
        "comarcas": [
            "Umuarama", "Alto Paraná", "Alto Piquiri", "Altônia", "Cianorte", "Cidade Gaúcha",
            "Cruzeiro do Oeste", "Goioerê", "Guaíra", "Icaraíma", "Iporã", "Loanda",
            "Nova Londrina", "Paraíso do Norte", "Paranavaí", "Pérola", "Santa Isabel do Ivaí",
            "Terra Rica", "Terra Roxa", "Xambrê"
        ]
    },
    "RAJ 8 - Maringá": {
        "numero": 8,
        "sede": "Maringá",
        "comarcas": [
            "Maringá", "Astorga", "Barbosa Ferraz", "Campo Mourão", "Centenário do Sul",
            "Colorado", "Engenheiro Beltrão", "Jaguapitã", "Jandaia do Sul", "Mandaguaçu",
            "Mandaguari", "Marialva", "Nova Esperança", "Paiçandu", "Paranacity",
            "Peabiru", "Santa Fé", "São João do Ivaí", "Sarandi", "Terra Boa"
        ]
    },
    "RAJ 9 - Londrina": {
        "numero": 9,
        "sede": "Londrina",
        "comarcas": [
            "Londrina", "Congonhinhas", "Faxinal", "Grandes Rios", "Marilândia do Sul",
            "Nova Fátima", "Ortigueira", "Primeiro de Maio", "São Jerônimo da Serra",
            "Sertanópolis", "Uraí", "Apucarana", "Arapongas", "Assaí", "Bela Vista do Paraíso",
            "Cambé", "Cornélio Procópio", "Ibiporã", "Porecatu", "Rolândia"
        ]
    },
    "RAJ 10 - Jacarezinho": {
        "numero": 10,
        "sede": "Jacarezinho",
        "comarcas": [
            "Jacarezinho", "Arapoti", "Cambará", "Carlópolis", "Curiúva", "Joaquim Távora",
            "Ribeirão Claro", "Ribeirão do Pinhal", "Santa Mariana", "Siqueira Campos",
            "Tomazina", "Andirá", "Bandeirantes", "Ibaiti", "Santo Antônio da Platina",
            "Wenceslau Braz"
        ]
    }
}


def get_raj_nome_curto(raj_nome_completo):
    """
    Extrai nome curto da RAJ.

    Args:
        raj_nome_completo: Nome completo da RAJ (ex: "RAJ 1 - Região Metropolitana de Curitiba e Litoral")

    Returns:
        Nome curto (ex: "Curitiba e Litoral")
    """
    if " - " in raj_nome_completo:
        return raj_nome_completo.split(" - ", 1)[1]
    return raj_nome_completo
