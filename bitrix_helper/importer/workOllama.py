from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM



model = OllamaLLM(model="llama3.2",
                #   base_url='http://ollama.bitrix-helper.orb.local:11434',
                  temperature=0.8
                  )


def answer_olama(promt,text):
  
  question=f'{promt}\n' + f'{text}'
  # print(question)
  ansewr=model.invoke(input=question, temperature=0.8)

  print(ansewr)