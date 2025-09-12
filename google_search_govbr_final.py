# Importações necessárias para o Selenium e outras funcionalidades
from selenium import webdriver  # Biblioteca principal para automação web
from selenium.webdriver.common.by import By  # Classe para localizar elementos na página
from selenium.webdriver.common.keys import Keys  # Classe para simular teclas do teclado
from selenium.webdriver.chrome.service import Service  # Serviço para gerenciar o ChromeDriver
from selenium.webdriver.chrome.options import Options  # Opções de configuração do Chrome
import time  # Biblioteca para pausas e delays
import json  # Biblioteca para formatação de dados em JSON
import random  # Biblioteca para gerar números aleatórios (simular comportamento humano)

def buscar_google_govbr():
    """
    🎯 FUNÇÃO PRINCIPAL: Busca no Google pelo termo 'gov.br' 
    
    Esta função automatiza uma busca no Google e coleta informações dos resultados:
    - Abre o navegador Chrome de forma invisível (headless)
    - Acessa o Google e realiza a busca por 'gov.br'
    - Coleta o título e URL de cada resultado da primeira página
    - Retorna uma lista estruturada com os dados coletados
    
    Returns:
        list: Lista de dicionários no formato [{"titulo": "...", "url": "..."}]
    """
    
    # 🔧 CONFIGURAÇÃO DO NAVEGADOR CHROME
    chrome_options = Options()  # Cria objeto de opções do Chrome
    
    # Configurações para execução invisível e otimizada:
    chrome_options.add_argument('--headless')  # Executar sem interface gráfica (invisível)
    chrome_options.add_argument('--disable-gpu')  # Desabilitar aceleração gráfica (evita erros)
    chrome_options.add_argument('--no-sandbox')  # Desabilitar sandbox (necessário em alguns sistemas)
    chrome_options.add_argument('--disable-dev-shm-usage')  # Evitar problemas de memória
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Ocultar automação
    chrome_options.add_argument('--disable-logging')  # Desabilitar logs verbosos
    chrome_options.add_argument('--silent')  # Modo silencioso
    
    # Configurações avançadas para parecer mais humano:
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Remove flag de automação
    chrome_options.add_experimental_option('useAutomationExtension', False)  # Desabilita extensão de automação
    # User-Agent real do Chrome para parecer um usuário normal:
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Inicializar o serviço e o navegador
    service = Service()  # Cria serviço padrão do ChromeDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)  # Inicia o Chrome com as configurações
    
    # 🕵️ MASCARAR AUTOMAÇÃO - Remove propriedade que identifica bots
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    resultados = []  # Lista para armazenar os resultados coletados

    try:
        # 🌐 ACESSAR O GOOGLE
        print("Acessando Google...")
        driver.get('https://www.google.com')  # Navega para a página inicial do Google
        
        # ⏱️ AGUARDAR CARREGAMENTO - Pausa aleatória para simular comportamento humano
        time.sleep(random.uniform(2, 3))  # Espera entre 2 e 3 segundos
        
        # 🍪 ACEITAR COOKIES (se aparecer o popup)
        try:
            # Procura botão de aceitar cookies em português ou inglês
            aceitar_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceitar') or contains(text(), 'Accept')]")
            aceitar_btn.click()  # Clica no botão
            time.sleep(1)  # Aguarda 1 segundo após clicar
        except:
            pass  # Se não encontrar o botão, continua (não é obrigatório)
        
        # 🔍 LOCALIZAR CAIXA DE BUSCA
        search_box = driver.find_element(By.NAME, 'q')  # Encontra campo de busca pelo atributo 'name'
        
        # ⌨️ SIMULAR DIGITAÇÃO HUMANA
        search_box.clear()  # Limpa qualquer texto existente
        termo = "gov.br"  # Define o termo de busca
        
        # Digita cada caractere com delay aleatório para parecer humano:
        for char in termo:
            search_box.send_keys(char)  # Digita um caractere
            time.sleep(random.uniform(0.05, 0.1))  # Pausa entre 0.05 e 0.1 segundos
        
        time.sleep(1)  # Pausa antes de pressionar Enter
        search_box.send_keys(Keys.RETURN)  # Pressiona Enter para buscar
        
        # ⏳ AGUARDAR RESULTADOS DA BUSCA
        print("Aguardando resultados...")
        time.sleep(random.uniform(3, 4))  # Aguarda entre 3 e 4 segundos para carregar
        
        # 🚫 VERIFICAR SE FOI BLOQUEADO PELO GOOGLE
        if 'sorry' in driver.current_url:
            print("❌ Google bloqueou a requisição.")
            return []  # Retorna lista vazia se foi bloqueado
        
        print("Coletando resultados...")
        
        # 🎯 LOCALIZAR ELEMENTOS DOS RESULTADOS
        # Primeira tentativa - seletor mais específico:
        elementos = driver.find_elements(By.CSS_SELECTOR, 'div.yuRUbf h3')
        
        # Se não encontrou, tenta seletor alternativo:
        if not elementos:
            elementos = driver.find_elements(By.CSS_SELECTOR, 'div.g h3')
        
        # Se ainda não encontrou, tenta seletor genérico:
        if not elementos:
            elementos = driver.find_elements(By.CSS_SELECTOR, 'h3')
        
        print(f"Encontrados {len(elementos)} resultados")
        
        # 📋 PROCESSAR CADA RESULTADO (máximo 10 da primeira página)
        for i, elemento in enumerate(elementos[:10]):  # Limita a 10 resultados
            try:
                # 📝 EXTRAIR TÍTULO
                titulo = elemento.text.strip()  # Pega o texto e remove espaços extras
                
                # Validar título (deve ter pelo menos 5 caracteres):
                if not titulo or len(titulo) < 5:
                    continue  # Pula para o próximo se título inválido
                
                # 🔗 EXTRAIR URL DO RESULTADO
                url = None
                try:
                    # Método 1: Busca o container pai do resultado
                    container = elemento.find_element(By.XPATH, "./ancestor::div[contains(@class,'g') or contains(@class,'yuRUbf')][1]")
                    link = container.find_element(By.TAG_NAME, 'a')  # Encontra o link dentro do container
                    url = link.get_attribute('href')  # Extrai a URL
                except:
                    try:
                        # Método 2: Verifica se o elemento pai é um link
                        parent = elemento.find_element(By.XPATH, "..")  # Pega elemento pai
                        if parent.tag_name == 'a':  # Se o pai for um link
                            url = parent.get_attribute('href')  # Extrai a URL
                    except:
                        continue  # Se não conseguir extrair URL, pula resultado
                
                # ✅ VALIDAR E FILTRAR URLs
                if (url and url.startswith('http') and  # URL deve começar com http
                    'google.com/url' not in url and  # Não deve ser link interno do Google
                    'webcache.googleusercontent.com' not in url):  # Não deve ser cache do Google
                    
                    # 📦 CRIAR DICIONÁRIO COM O RESULTADO
                    resultado = {
                        'titulo': titulo,  # Título da página
                        'url': url        # URL da página
                    }
                    resultados.append(resultado)  # Adiciona à lista de resultados
                    print(f"✓ Coletado: {titulo[:50]}...")  # Mostra os primeiros 50 caracteres do título
                    
            except Exception as e:
                continue  # Se houver erro com um resultado, continua para o próximo
        
        # 📊 MOSTRAR ESTATÍSTICAS FINAIS
        print(f"\nTotal de resultados coletados: {len(resultados)}")
        return resultados  # Retorna lista com todos os resultados coletados
        
    except Exception as e:
        # 🚨 TRATAMENTO DE ERROS GERAIS
        print(f"Erro: {e}")
        return []  # Retorna lista vazia em caso de erro
    
    finally:
        # 🧹 LIMPEZA - Sempre fecha o navegador, mesmo se houver erro
        driver.quit()

# 🚀 EXECUÇÃO PRINCIPAL DO PROGRAMA
if __name__ == "__main__":
    # Executa a função de busca:
    resultados = buscar_google_govbr()
    
    # 📋 EXIBIR RESULTADOS FORMATADOS
    if resultados:
        print("\n" + "="*60)
        print("RESULTADOS DA BUSCA 'gov.br' NO GOOGLE")
        print("="*60)
        # Exibe os resultados em formato JSON bonito:
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
    else:
        print("Nenhum resultado foi coletado.")
