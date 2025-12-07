"""
Script para gerar novos códigos de acesso
Mantém o código do admin (41997813606) e gera novos para todos os outros
"""
import random
import string
import re
from datetime import datetime

# Ler arquivo atual
with open('app.py', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Extrair AUTH_CODES atual
match = re.search(r'AUTH_CODES = \{(.*?)\}', conteudo, re.DOTALL)
if not match:
    print("Erro: Não foi possível encontrar AUTH_CODES")
    exit(1)

auth_codes_texto = match.group(1)

# Parsear telefones e códigos atuais
telefones_codigos = {}
for line in auth_codes_texto.strip().split('\n'):
    line = line.strip()
    if line and ':' in line:
        # Formato: "41988682140": "TJPR-W9D8A6",
        parts = line.replace('"', '').replace(',', '').split(':')
        if len(parts) == 2:
            telefone = parts[0].strip()
            codigo = parts[1].strip()
            telefones_codigos[telefone] = codigo

print(f"Total de telefones encontrados: {len(telefones_codigos)}")

# Salvar backup com timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = f"backup/auth_codes_backup_{timestamp}.txt"

with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(f"# BACKUP DOS CÓDIGOS DE ACESSO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"# Total de usuários: {len(telefones_codigos)}\n\n")
    f.write("AUTH_CODES = {\n")
    for telefone in sorted(telefones_codigos.keys()):
        f.write(f'    "{telefone}": "{telefones_codigos[telefone]}",\n')
    f.write("}\n")

print(f"[OK] Backup salvo em: {backup_file}")

# Gerar novos códigos
def gerar_codigo():
    """Gera código no formato TJPR-XXXXXX"""
    chars = string.ascii_uppercase + string.digits
    return 'TJPR-' + ''.join(random.choice(chars) for _ in range(6))

# Telefone do admin (manter código original)
ADMIN_TELEFONE = "41997813606"
admin_codigo_original = telefones_codigos.get(ADMIN_TELEFONE, "TJPR-F4F1X5")

# Gerar códigos únicos para todos (exceto admin)
novos_codigos = {}
codigos_usados = {admin_codigo_original}  # Manter código do admin

# Adicionar admin com código original
novos_codigos[ADMIN_TELEFONE] = admin_codigo_original

# Gerar novos códigos para todos os outros
for telefone in sorted(telefones_codigos.keys()):
    if telefone == ADMIN_TELEFONE:
        continue  # Já adicionado

    # Gerar código único
    while True:
        novo_codigo = gerar_codigo()
        if novo_codigo not in codigos_usados:
            codigos_usados.add(novo_codigo)
            novos_codigos[telefone] = novo_codigo
            break

print(f"[OK] Gerados {len(novos_codigos)} códigos (1 mantido do admin, {len(novos_codigos)-1} novos)")

# Criar arquivo com novos códigos
with open('backup/novos_codigos_' + timestamp + '.txt', 'w', encoding='utf-8') as f:
    f.write(f"# NOVOS CÓDIGOS DE ACESSO - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    f.write(f"# Total de usuários: {len(novos_codigos)}\n")
    f.write(f"# Admin (código mantido): {ADMIN_TELEFONE}\n\n")
    f.write("AUTH_CODES = {\n")
    for telefone in sorted(novos_codigos.keys()):
        marcador = " # ADMIN (código mantido)" if telefone == ADMIN_TELEFONE else ""
        f.write(f'    "{telefone}": "{novos_codigos[telefone]}",{marcador}\n')
    f.write("}\n")

print(f"[OK] Novos códigos salvos em: backup/novos_codigos_{timestamp}.txt")

# Gerar conteúdo Python formatado para substituição
print("\n" + "="*80)
print("NOVO AUTH_CODES PARA SUBSTITUIR NO app.py:")
print("="*80)
print()
print("AUTH_CODES = {")
for telefone in sorted(novos_codigos.keys()):
    marcador = "  # ADMIN (código mantido)" if telefone == ADMIN_TELEFONE else ""
    print(f'    "{telefone}": "{novos_codigos[telefone]}",{marcador}')
print("}")
