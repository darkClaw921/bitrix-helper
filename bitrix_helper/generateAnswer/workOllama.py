from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """Question: {question}

Answer: Let's think step by step."""

prompt = ChatPromptTemplate.from_template(template)

model = OllamaLLM(model="llama3.2",
                #   base_url='http://ollama.bitrix-helper.orb.local:11434',
                  )

chain = prompt | model

a=chain.invoke({"question": """	Abdul Rahman	arahman@epiqsystems.co.uk	Epiq	44 (0) 20 7367 9109	Active	"B-305 & C-306, Teerth Technospace, Mumbai Bangalore Highway, Next to B.U. Bhandari's Mercedes Benz Show Room
Baner, Pune, Maharashtra 411045
India"	Baner, Pune, Maharashtra		B-305 & C-306, Teerth Technospace, Mumbai Bangalore Highway, Next to B.U. Bhandari's Mercedes Benz Show Room			India	9102069000403		411045	No	No	No	No	No		No	No	No	No		No	India	No	No	No		No	No	No	India	Admin Sync360	10.08.2023 18:32		No	No	Senior Claims Analyst	No	No	Allow	No	Allow	Allow	Allow	Default Value				Not Validated	No	No	No	No	No	No	No	Abdul	No	Allow		Male	No	No	No	No	No	No	No	No	No	Legal Department	Application Support Analyst					Rahman	Default Value	No	No		No	No			Admin Sync360	23.08.2023 19:00	English, Hindi		seamless		No	No	No	No					Abdul Rahman				No	Send			No	No	No	No	No	No
переведи на русский"""})
print(a)