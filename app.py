import streamlit as st
import os, config
from llama_index import StorageContext, load_index_from_storage

#os.environ['OPENAI_API_KEY'] = config.OPENAI_API_KEY

def print_markdown_from_file(file_path):
    with open(file_path, "r") as f:
        markdown_content = f.read()
        st.markdown(markdown_content)

st.set_page_config(page_title="Edulisto, normativas sobre educación", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

st.image("./Edulisto_S.png")

st.title("Edulisto, te ayuda con las Normativas Educativas")
st.info("Lo sabe todo sobre EDUCACIÓN. Se ha estudiado toda las normativas, metodologías, y herramientas.")
         
if 'messages' not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Preguntame lo que quieras sobre EDUCACIÓN!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Cargando la base de conocimiento. Esto puede tardar unos segundos..."):
        # Cargamos la BBDD de Indices(Nodos, Vectores e Indices)
        storage_context = StorageContext.from_defaults(persist_dir="storage")
        index = load_index_from_storage(storage_context)
        return index

index = load_data()

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
    chat_engine = index.as_chat_engine(
        chat_mode="condense_plus_context",
        #memory=memory,
        #llm=llm,
        system_prompt=(
            "Eres un consultor en materia de educación especialista en normativa educativa"
            "Eres un profesor abogado y especialista en normativas educativas"
            "Sólo puedes responder a preguntas relacionadas con normativa educativa"
            "Para preguntas sobre otros temas, debes responder: ¡Creo que no es un tema relacionado con Educación o no me lo he estudiado!"
            "Debe utilizar exclusivamente la información faclititada por el usuario"
            ""
            ),
        verbose=True,
    )
    #st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_plus_context", verbose=True)
    st.session_state.chat_engine = chat_engine

if prompt := st.chat_input("Tu pregunta..."): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Deja que piense..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)

            # Include source nodes in the response
            st.write("Información de los nodos de origen:")
            for node in response.source_nodes:
                st.write(f"Fichero: {node.id}, Página: {node.page_number}")

            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
