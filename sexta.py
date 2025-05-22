import speech_recognition as sr
import pyttsx3
import wikipedia
import pywhatkit
import openai
import requests

# Configuração da API do OpenAI
openai.api_key = "???????"
model_engine = "gpt-3.5-Turbo"

# Dicionário de contatos
contatos = {
    "contato": "1",
    "contato": "2",
    "contato": "3",
    "contato": "4",
    "contato": "5",
    "contato": "6",
    
    }

# Inicializando reconhecimento de voz e fala
audio = sr.Recognizer()
maquina = pyttsx3.init()

def listen_command():
    """Escuta o comando de voz"""
    try:
        with sr.Microphone() as source:
            print('Escutando...')
            audio.adjust_for_ambient_noise(source)
            voz = audio.listen(source)
            comando = audio.recognize_google(voz, language='pt-BR')
            comando = comando.lower()

            if 'sexta-feira' in comando:
                comando = comando.replace('sexta-feira', '')
                maquina.say('Estou ouvindo.')
                maquina.runAndWait()

            comando = comando.strip()
            if not comando:
                return ''  # Caso o comando seja vazio após a troca, retorna vazio
            return comando
    except Exception as e:
        print(f'Um erro inesperado aconteceu: {e}')
        return ''

# Função para obter latitude e longitude de uma cidade usando OpenCage Geocoder
def obter_lat_long(cidade):
    """Retorna latitude e longitude da cidade fornecida"""
    chave_api = "0b45b09a74c7415f847e49e218bf516f"  # Coloque sua chave API aqui
    url = f"https://api.opencagedata.com/geocode/v1/json?q={cidade}&key={chave_api}&language=pt&pretty=1"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        if dados['results']:
            latitude = dados['results'][0]['geometry']['lat']
            longitude = dados['results'][0]['geometry']['lng']
            return latitude, longitude
        else:
            return None, None
    except Exception as e:
        return None, None

# Função para obter o clima com Open-Meteo usando a cidade fornecida
def obter_clima(cidade):
    """Obtém o clima atual de uma cidade usando Open-Meteo"""
    latitude, longitude = obter_lat_long(cidade)
    if latitude is None or longitude is None:
        return "Não consegui encontrar a localização dessa cidade."

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&temperature_unit=celsius&windspeed_unit=kmh&precipitation_unit=mm&timezone=America/Sao_Paulo"
    
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        temperatura = dados["current_weather"]["temperature"]
        condicao = dados["current_weather"]["weathercode"]

        if condicao == 0:
            condicao_texto = "ensolarado"
        else:
            condicao_texto = "nublado"

        return f"A temperatura atual em {cidade} é de {temperatura}°C com tempo {condicao_texto}."
    except Exception as e:
        return f"Erro ao acessar a API de clima: {e}"

def conversar_com_openai(pergunta):
    """Conversa com o ChatGPT"""
    completion = openai.ChatCompletion.create(
        model=model_engine,
        messages=[{"role": "user", "content": pergunta}]
    )
    resposta = completion.choices[0].message['content']
    return resposta

def execute_command():
    comando = listen_command()
    if not comando:
        return

    # Procurar por algo na Wikipedia
    if 'procure por' in comando or 'pesquise por' in comando:
        procurar = comando.replace('procure por', '').replace('pesquise por', '').strip()
        wikipedia.set_lang('pt')
        try:
            resultado = wikipedia.summary(procurar, sentences=2)
            if resultado:
                print(resultado)
                maquina.say(resultado)
                maquina.runAndWait()
            else:
                maquina.say('Não encontrei nada sobre isso.')
                maquina.runAndWait()
        except wikipedia.exceptions.DisambiguationError:
            maquina.say('Muitos resultados encontrados. Seja mais específico.')
            maquina.runAndWait()
        except wikipedia.exceptions.PageError:
            maquina.say('Não encontrei nada sobre isso.')
            maquina.runAndWait()

    # Tocar música no YouTube
    elif 'toque' in comando:
        musica = comando.replace('toque', '').strip()
        if musica:
            pywhatkit.playonyt(musica)
            maquina.say(f'Tocando {musica} no YouTube.')
            maquina.runAndWait()
        else:
            maquina.say('Desculpe, não encontrei nenhuma música para tocar.')
            maquina.runAndWait()
 # Mandar mensagem para contato
    elif 'mandar mensagem para' in comando:
        try:
            nome_contato = comando.replace('mandar mensagem para', '').strip()
            
            numero = contatos.get(nome_contato)

            if numero:
                maquina.say(f'Qual mensagem você deseja enviar para {nome_contato}?')
                maquina.runAndWait()
                mensagem = listen_command()

                pywhatkit.sendwhatmsg_instantly(f"+55{numero}", mensagem)
                maquina.say('Mensagem enviada com sucesso!')
                maquina.runAndWait()
            else:
                maquina.say("Contato não encontrado. Tente novamente.")
                maquina.runAndWait()
        except Exception as e:
            maquina.say(f"Ocorreu um erro ao enviar a mensagem: {e}")

            maquina.runAndWait()

    # Respostas usando OpenAI
    elif 'responda' in comando or 'fale sobre' in comando or 'crie' in comando or 'o que você acha sobre' in comando:
        prompt = comando.replace('responda', '').replace('fale sobre', '').replace('crie', '').replace('o que você acha sobre', '').strip()
        if prompt:
            resposta = conversar_com_openai(prompt)
            print(resposta)
            maquina.say(resposta)
            maquina.runAndWait()

    # Verificar o clima
    elif 'clima de' in comando or 'tempo de' in comando:
        cidade = comando.replace('clima de', '').replace('tempo de', '').strip()
        if cidade:
            clima = obter_clima(cidade)  # Chama a função para obter o clima
            print(clima)
            maquina.say(clima)
            maquina.runAndWait()

    # Comando para encerrar
    elif 'encerrar' in comando:
        maquina.say("Até logo!")
        maquina.runAndWait()
        return False  # Para sair do loop
    return True  # Continua o loop

if __name__ == '__main__':
    while True:
        if not execute_command():
            break  # Se o comando for 'encerrar', sai do loop
