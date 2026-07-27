import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===============================================================
# CONFIGURAÇÃO LOCAL PARA TESTES
# ===============================================================
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
URL_MOCK = f"file:///{PASTA_ATUAL.replace('\\', '/')}/index.html"
USER_LOGIN = "gasoliveseo4"
USER_PASSWORD = "minhasenhaprotegida"

def configurar_driver():
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--start-maximized")
    opcoes.add_experimental_option("excludeSwitches", ["enable-automation"])
    opcoes.add_experimental_option("useAutomationExtension", False)
    opcoes.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opcoes
    )

    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

def encontrar_elemento_por_varios_seletores(driver, xpath_list, timeout=5):
    for xpath in xpath_list:
        try:
            elemento = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if elemento.is_displayed():
                return elemento
        except:
            continue
    return None

def encontrar_elementos_por_varios_seletores(driver, xpath_list, timeout=5):
    for xpath in xpath_list:
        try:
            elementos = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            visiveis = [e for e in elementos if e.is_displayed()]
            if visiveis:
                return visiveis
        except:
            continue
    return []

def localizar_campo_url_antiga(driver):
    xpaths = [
        "//input[contains(@placeholder, 'URL antiga')]",
        "//label[contains(text(), 'URL antiga')]/following::input[1]",
        "//label[contains(text(), 'URL antiga')]/following-sibling::input",
        "//input[@name='url_antiga' or @id='url_antiga' or @name='urlAntiga']",
        "(//input[@type='text' or not(@type)])[1]"
    ]
    return encontrar_elemento_por_varios_seletores(driver, xpaths)

def localizar_campo_url_nova(driver):
    xpaths = [
        "//input[contains(@placeholder, 'URL nova')]",
        "//label[contains(text(), 'URL nova')]/following::input[1]",
        "//label[contains(text(), 'URL nova')]/following-sibling::input",
        "//input[@name='url_nova' or @id='url_nova' or @name='urlNova']",
        "(//input[@type='text' or not(@type)])[2]"
    ]
    return encontrar_elemento_por_varios_seletores(driver, xpaths)

def localizar_botao_salvar(driver):
    xpaths = [
        "//button[contains(text(), 'Salvar')]",
        "//*[text()='Salvar']",
        "//input[@type='submit' and @value='Salvar']",
        "//button[contains(@class, 'blue') or contains(@class, 'primary') or contains(@class, 'salvar')]"
    ]
    return encontrar_elemento_por_varios_seletores(driver, xpaths)

def realizar_login_moovin(driver):
    print(f"\n🔐 Acessando simulador de login: {URL_MOCK}")
    driver.get(URL_MOCK)
    
    # 1. Campo de Login
    print("   Inserindo login...")
    campo_user = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'login') or @name='login' or @id='UsuarioLogin_login']"))
    )
    campo_user.clear()
    campo_user.send_keys(USER_LOGIN)

    # 2. Campo de Senha
    print("   Inserindo senha...")
    campo_senha = driver.find_element(By.XPATH, "//input[@type='password' or @id='UsuarioLogin_senha']")
    campo_senha.clear()
    campo_senha.send_keys(USER_PASSWORD)

    # 3. Clicar em Entrar
    print("   Clicando em Entrar...")
    botao_entrar = driver.find_element(By.XPATH, "//button[contains(text(), 'Entrar') or @id='UsuarioSubmit']")
    botao_entrar.click()
    
    # 4. Verificação de 2 etapas (2FA)
    print("\n🔑 Carregando tela de 2FA...")
    time.sleep(1.5)

    print("ℹ️ Dica: Para o teste local, você pode digitar qualquer código de 6 dígitos.")
    codigo_2fa = input("👉 Digite um código de 6 dígitos para o 2FA: ").strip()
    while len(codigo_2fa) != 6 or not codigo_2fa.isdigit():
        codigo_2fa = input("⚠️ Digite exatamente 6 dígitos: ").strip()

    # Preenche os 6 inputs
    inputs_2fa = encontrar_elementos_por_varios_seletores(driver, [
        "//input[contains(@class, 'code') or @type='text' or @type='tel']"
    ], timeout=10)

    if len(inputs_2fa) >= 6:
        print("   Digitando código de teste nos campos do 2FA...")
        for j, digito in enumerate(codigo_2fa):
            inputs_2fa[j].clear()
            inputs_2fa[j].send_keys(digito)
            time.sleep(0.1)
    else:
        print("   Inserindo código no campo fallback do 2FA...")
        if inputs_2fa:
            inputs_2fa[0].send_keys(codigo_2fa)

    # Clicar em Continuar
    print("   Confirmando 2FA...")
    botao_continuar = encontrar_elemento_por_varios_seletores(driver, [
        "//button[contains(text(), 'Continuar') or @id='btn-confirmar-2fa']"
    ], timeout=5)
    
    if botao_continuar:
        botao_continuar.click()

    print("   ✓ Login realizado!")
    time.sleep(1)

def navegar_ate_redirecionamentos(driver):
    print("\n📂 Navegando pelo menu lateral do painel de testes...")
    
    # Clicar em Ferramentas
    xpath_ferramentas = [
        "//*[contains(text(), 'Ferramentas')]"
    ]
    menu_ferramentas = encontrar_elemento_por_varios_seletores(driver, xpath_ferramentas, timeout=10)
    if not menu_ferramentas:
        raise Exception("Menu 'Ferramentas' não encontrado.")
    menu_ferramentas.click()
    time.sleep(0.5)

    # Clicar em Redirecionamentos
    xpath_redirecionamentos = [
        "//*[contains(text(), 'Redirecionamentos')]"
    ]
    item_redirecionamentos = encontrar_elemento_por_varios_seletores(driver, xpath_redirecionamentos, timeout=10)
    if not item_redirecionamentos:
        raise Exception("Opção 'Redirecionamentos' não encontrada.")
    item_redirecionamentos.click()
    time.sleep(1)

def main():
    print("=" * 60)
    print("        SCRIPT DE VALIDAÇÃO LOCAL (TESTE-MOOVIN)")
    print("=" * 60)

    caminho_csv = os.path.join(PASTA_ATUAL, "redirecionamentos.csv")
    
    # Lê o CSV
    redirecionamentos = []
    with open(caminho_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for linha in reader:
            if 'url_antiga' in linha and 'url_nova' in linha:
                redirecionamentos.append({
                    'antiga': linha['url_antiga'].strip(),
                    'nova': linha['url_nova'].strip()
                })
    
    print(f"📊 CSV carregado com {len(redirecionamentos)} linhas.")

    driver = configurar_driver()
    
    try:
        # Executa Login e 2FA
        realizar_login_moovin(driver)

        # Navega no menu
        navegar_ate_redirecionamentos(driver)

        # Clica em Cadastrar
        print("\n🖱️ Procurando o botão 'Cadastrar'...")
        botao_cadastrar = encontrar_elemento_por_varios_seletores(driver, [
            "//button[contains(text(), 'Cadastrar') or @id='btn-cadastrar-redirect']"
        ], timeout=10)
        
        botao_cadastrar.click()
        print("   ✓ Botão 'Cadastrar' clicado!")
        time.sleep(1)

        sucessos = 0
        erros = 0
        lista_erros = []

        # Loop de preenchimento
        for i, red in enumerate(redirecionamentos, start=1):
            print(f"\n🔄 [{i}/{len(redirecionamentos)}] Processando: {red['antiga']} ➡️ {red['nova']}")
            
            try:
                campo_antiga = localizar_campo_url_antiga(driver)
                campo_nova = localizar_campo_url_nova(driver)
                botao_salvar = localizar_botao_salvar(driver)

                if not campo_antiga or not campo_nova or not botao_salvar:
                    raise Exception("Campos ou botão 'Salvar' não localizados.")

                # Preenche URL Antiga
                campo_antiga.click()
                campo_antiga.send_keys(Keys.CONTROL + "a")
                campo_antiga.send_keys(Keys.DELETE)
                campo_antiga.send_keys(red['antiga'])
                time.sleep(0.2)

                # Preenche URL Nova
                campo_nova.click()
                campo_nova.send_keys(Keys.CONTROL + "a")
                campo_nova.send_keys(Keys.DELETE)
                campo_nova.send_keys(red['nova'])
                time.sleep(0.2)

                # Clica em Salvar
                botao_salvar.click()
                print("   Enviando...")
                time.sleep(1)

                # Verifica modal de feedback
                texto_pagina = driver.find_element(By.TAG_NAME, "body").text
                
                if "sucesso" in texto_pagina.lower():
                    sucessos += 1
                    print("   ✅ Sucesso cadastrado!")
                else:
                    mensagem_erro = "Erro genérico ou URL duplicada"
                    if "já existe" in texto_pagina.lower():
                        mensagem_erro = "Já existe um redirecionamento com a URL antiga informada!"
                    
                    erros += 1
                    lista_erros.append({
                        "antiga": red['antiga'],
                        "nova": red['nova'],
                        "erro": mensagem_erro
                    })
                    print(f"   ❌ Erro detectado: {mensagem_erro}")

                # Clica no OK do modal para liberar tela
                botao_ok = encontrar_elemento_por_varios_seletores(driver, [
                    "//button[text()='OK' or @class='btn-modal-ok']"
                ], timeout=5)
                if botao_ok:
                    botao_ok.click()
                    time.sleep(0.5)

            except Exception as e:
                erros += 1
                lista_erros.append({
                    "antiga": red['antiga'],
                    "nova": red['nova'],
                    "erro": str(e)
                })
                print(f"   ❌ Erro na linha: {e}")
                time.sleep(1)

        # Relatório Final
        print("\n" + "=" * 60)
        print("🏁 VALIDAÇÃO LOCAL CONCLUÍDA COM SUCESSO!")
        print(f"   ✓ Sucessos: {sucessos}")
        print(f"   ✗ Erros: {erros}")
        print("=" * 60)

        if lista_erros:
            print("\nLista de Falhas Simuladas:")
            for idx, item in enumerate(lista_erros, start=1):
                print(f" {idx}. '{item['antiga']}' ➡️ '{item['nova']}'")
                print(f"    Motivo: {item['erro']}")
            print("=" * 60)

    except Exception as e:
        print(f"\n❌ Falha geral na execução do teste: {e}")

    input("\n🔲 Pressione ENTER para fechar o navegador de testes...")
    driver.quit()

if __name__ == "__main__":
    main()
