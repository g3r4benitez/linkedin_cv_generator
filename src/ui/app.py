"""Interfaz Streamlit para LinkedIn CV Generator."""
import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Agregar raíz del proyecto al path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.data.linkedin_pdf_parser import LinkedInPDFParser
from src.ai.resume_generator import ResumeGenerator

# Configuración de la página
st.set_page_config(
    page_title="LinkedIn CV Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos personalizados
st.markdown("""
<style>
    .main {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        border-radius: 5px;
        height: 40px;
    }
    .uploadedFile {
        border: 1px dashed #ccc;
        border-radius: 5px;
        padding: 20px;
        text-align: center;
    }
    .success-message {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .info-message {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .warning-message {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 10px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📄 LinkedIn CV Generator")
    st.markdown("Genera currículums optimizados para ofertas de trabajo usando tus datos de LinkedIn")
    
    # Estado de la sesión para datos del perfil
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = None
    if 'generated_cv' not in st.session_state:
        st.session_state.generated_cv = None
    if 'github_highlights' not in st.session_state:
        st.session_state.github_highlights = None
    
    # Sidebar con navegación
    page = st.sidebar.selectbox(
        "Selecciona una opción:",
        ["🏠 Inicio", "📤 Subir LinkedIn PDF", "💼 GitHub Integration", "📝 Generar CV", "📂 Archivos Generados"]
    )
    
    if page == "🏠 Inicio":
        show_welcome()
    elif page == "📤 Subir LinkedIn PDF":
        upload_linkedin_pdf()
    elif page == "💼 GitHub Integration":
        github_integration()
    elif page == "📝 Generar CV":
        generate_resume_page()
    elif page == "📂 Archivos Generados":
        show_generated_files()

def show_welcome():
    st.markdown("""
    ## Bienvenido a LinkedIn CV Generator
    
    Esta herramienta te ayuda a convertir tu perfil de LinkedIn en currículums optimizados para ofertas de trabajo.
    
    ### Funcionalidades:
    
    1. **Extrae datos de LinkedIn**: Sube tu PDF exportado de LinkedIn
    2. **Integra GitHub**: Conecta con tu perfil de GitHub para proyectos destacados
    3. **Optimiza con IA**: Adapta tu CV a ofertas específicas usando OpenAI
    4. **Genera múltiples formatos**: HTML y PDF descargables
    
    ### Cómo usarlo:
    
    1. En "📤 Subir LinkedIn PDF", carga tu PDF exportado de LinkedIn
    2. Opcional: Conecta tu GitHub en "💼 GitHub Integration"
    3. En "📝 Generar CV", ingresa una job description y genera tu CV
    4. Descarga el CV generado
    """)
    
    if st.session_state.profile_data:
        st.markdown(f"### ✅ Datos cargados: {st.session_state.profile_data.get('name', 'Perfil')}")
        st.json(st.session_state.profile_data)

def upload_linkedin_pdf():
    st.header("📤 Subir PDF de LinkedIn")
    
    uploaded_file = st.file_uploader(
        "Selecciona tu PDF exportado de LinkedIn", 
        type=["pdf"],
        help="Exporta tu perfil desde LinkedIn: Me > Privacidad y configuración > Obtener enlace para compartir > Exportar perfil"
    )
    
    if uploaded_file is not None:
        with st.spinner("Procesando PDF de LinkedIn..."):
            # Guardar archivo temporalmente
            temp_path = os.path.join("assets", "temp_upload.pdf")
            os.makedirs("assets", exist_ok=True)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Parsear PDF
            parser = LinkedInPDFParser(temp_path)
            profile_data = parser.parse()
            parser.save_json("parsed_linkedin_profile.json")
            
            st.session_state.profile_data = profile_data
            
            st.markdown("""
            <div class="success-message">
                ✅ PDF procesado exitosamente!
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar resumen
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Información Básica")
                st.write(f"**Nombre:** {profile_data.get('name', 'No disponible')}")
                st.write(f"**Headline:** {profile_data.get('headline', 'No disponible')[:60]}...")
                st.write(f"**Email:** {profile_data.get('contact_info', {}).get('email', 'No disponible')}")
                st.write(f"**Teléfono:** {profile_data.get('contact_info', {}).get('phone', 'No disponible')}")
            
            with col2:
                st.subheader("Datos Extraídos")
                st.write(f"**Skills:** {len(profile_data.get('skills', []))} encontradas")
                st.write(f"**Experiencia:** {len(profile_data.get('experience', []))} trabajos")
                st.write(f"**Educación:** {len(profile_data.get('education', []))} estudios")
                st.write(f"**Idiomas:** {len(profile_data.get('languages', []))} detectados")
            
            # Mostrar skills extraídas
            if profile_data.get('skills'):
                st.subheader("Habilidades Técnicas Encontradas")
                skills_html = ", ".join([f"`{skill}`" for skill in profile_data['skills']])
                st.markdown(skills_html)
            
            st.success("¡Datos listos para usar! Ahora ve a '📝 Generar CV' para crear tu currículum.")

def github_integration():
    st.header("💼 GitHub Integration")
    
    github_token = st.text_input(
        "GitHub Token (opcional)",
        placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        help="Token de acceso personal. Puedes obtenerlo en: https://github.com/settings/tokens"
    )
    
    username = st.text_input(
        "Username de GitHub",
        placeholder="gerardobenitez"
    )
    
    if github_token and username:
        with st.spinner("Extrayendo información de GitHub..."):
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
                from src.data.github_extractor import GitHubExtractor
                
                extractor = GitHubExtractor(token=github_token)
                github_data = extractor.extract_profile(username)
                extractor.save_json(github_data, "github_profile_data.json")
                
                st.session_state.github_highlights = extractor.generate_github_highlights(github_data)
                
                st.markdown("""
                <div class="success-message">
                    ✅ Información de GitHub extraída exitosamente!
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar highlights
                highlights = st.session_state.github_highlights
                st.subheader("Resumen de GitHub")
                st.write(f"**Repositorios públicos:** {highlights.get('total_repos', 0)}")
                st.write(f"**Seguidores:** {highlights.get('total_followers', 0)}")
                st.write(f"**Contribuciones (último año):** {highlights.get('recent_contributions', 0)}")
                
                if highlights.get('top_languages'):
                    st.write(f"**Lenguajes principales:** {', '.join(highlights['top_languages'])}")
                
                # Proyectos destacados
                if highlights.get('featured_projects'):
                    st.subheader("Proyectos Destacados")
                    for project in highlights['featured_projects']:
                        with st.expander(f"⭐ {project['name']} ({project.get('stars', 0)} stars)"):
                            st.write(f"**Lenguaje:** {project.get('language', 'N/A')}")
                            if project.get('description'):
                                st.write(f"**Descripción:** {project['description']}")
                            st.markdown(f"[Ver en GitHub]({project.get('url', '#')})")
                
            except Exception as e:
                st.error(f"❌ Error al extraer información de GitHub: {str(e)}")
    else:
        st.info("Ingresa tu token de GitHub y username para integrar información de proyectos")
        st.markdown("""
        <div class="info-message">
            ℹ️ Puedes obtener tu token en: https://github.com/settings/tokens
            <br>Permisos necesarios: read:user, repo
        </div>
        """, unsafe_allow_html=True)

def generate_resume_page():
    st.header("📝 Generar Currículum")
    
    if not st.session_state.profile_data:
        st.warning("⚠️ Primero debes subir tu PDF de LinkedIn en la sección '📤 Subir LinkedIn PDF'")
        return
    
    profile_data = st.session_state.profile_data
    
    # Integrar highlights de GitHub si existen
    if st.session_state.github_highlights:
        profile_data["github_highlights"] = st.session_state.github_highlights
        profile_data["github_username"] = "gerardobenitez"
    
    # Input de job description
    st.subheader("📄 Job Description")
    job_description = st.text_area(
        "Pega aquí la descripción del trabajo",
        height=200,
        placeholder="Ej: Buscamos Senior Backend Engineer con experiencia en Python, FastAPI, AWS, Docker..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        format_option = st.selectbox(
            "Formato de salida",
            options=["HTML", "PDF"],
            index=0
        )
    
    with col2:
        language_option = st.selectbox(
            "Idioma del CV",
            options=["Español", "English"],
            index=0
        )
    
    # Opciones avanzadas
    with st.expander("⚙️ Opciones Avanzadas"):
        st.write("Estas opciones requieren API key de OpenAI configurada")
        use_ai_optimization = st.checkbox(
            "Optimizar con IA", 
            value=False,
            help="Usar OpenAI para optimizar el CV según keywords de la oferta"
        )
    
    if st.button("🚀 Generar CV", type="primary"):
        if use_ai_optimization and not job_description.strip():
            st.warning("⚠️ Para optimizar con IA, debes ingresar una job description.")
            return
        with st.spinner("Generando currículum..."):
            try:
                generator = ResumeGenerator()
                
                if use_ai_optimization and not generator.job_analyzer:
                    st.error("❌ No se encontró la API key de OpenAI. Configúrala en el archivo `.env` con `OPENAI_API_KEY`")
                    return
                
                # Generar CV
                html_resume = generator.generate_resume(
                    profile_data, 
                    job_description if job_description.strip() else None,
                    use_ai=use_ai_optimization,
                    language="es" if language_option == "Español" else "en"
                )
                
                # Mostrar matching scores si se uso IA
                if use_ai_optimization and job_description.strip() and generator.job_analyzer:
                    with st.spinner("Calculando matching score..."):
                        job_data = generator.job_analyzer.analyze_job_description(job_description, "es" if language_option == "Español" else "en")
                        job_data = generator.job_analyzer._normalize_job_data(job_data)
                        matching = generator.job_analyzer.generate_keyword_matching(profile_data, job_data)
                        
                        st.subheader("📊 Matching Score")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Habilidades", f"{matching.get('matching_skills', 0)}%")
                        with col2:
                            st.metric("Experiencia", f"{matching.get('matching_experience', 0)}%")
                        with col3:
                            st.metric("Título", f"{matching.get('matching_title', 0)}%")
                        with col4:
                            st.metric("Seniority", f"{matching.get('matching_seniority', 0)}%")
                
                st.session_state.generated_cv = html_resume
                
                # Generar en formato solicitado
                output_format = format_option.lower() if format_option == "HTML" else "pdf"
                filename = f"cv_gerardobenitez_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"
                
                filepath = generator.save_resume(html_resume, output_format, filename)
                
                st.markdown("""
                <div class="success-message">
                    ✅ ¡Currículum generado exitosamente!
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar preview
                st.subheader("📋 Preview del CV")
                
                if output_format == "html":
                    with st.expander("Ver HTML generado"):
                        st.code(html_resume[:2000] + "..." if len(html_resume) > 2000 else html_resume, language="html")
                else:
                    st.success(f"PDF generado correctamente")
                
                # Botón de descarga según formato
                if output_format == "html":
                    st.download_button(
                        label="📥 Descargar CV (HTML)",
                        data=html_resume,
                        file_name=filename,
                        mime="text/html",
                        type="primary"
                    )
                else:
                    # Para PDF, usar el archivo generado
                    with open(filepath, "rb") as f:
                        pdf_data = f.read()
                    st.download_button(
                        label="📥 Descargar CV (PDF)",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary"
                    )
                
                st.success(f"Archivo guardado en: `cvs_generados/{filename}`")
                
            except Exception as e:
                st.error(f"❌ Error generando CV: {str(e)}")
                import traceback
                with st.expander("Detalles del error"):
                    st.code(traceback.format_exc())

def show_generated_files():
    st.header("📂 Archivos Generados")
    
    cvs_dir = os.path.join(os.path.dirname(__file__), "..", "cvs_generados")
    
    if not os.path.exists(cvs_dir):
        st.info("Aún no se han generado archivos.")
        return
    
    files = [f for f in os.listdir(cvs_dir) if f.endswith(('.html', '.pdf'))]
    
    if not files:
        st.info("No hay archivos generados todavía.")
        return
    
    for file in files:
        filepath = os.path.join(cvs_dir, file)
        file_size = os.path.getsize(filepath)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"📄 **{file}**")
        
        with col2:
            st.write(f"{file_size // 1024} KB")
        
        with col3:
            with open(filepath, "rb") as f:
                st.download_button(
                    label="⬇️",
                    data=f,
                    file_name=file,
                    mime="text/html" if file.endswith('.html') else "application/pdf",
                    key=file
                )

if __name__ == "__main__":
    main()