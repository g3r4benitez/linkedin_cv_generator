# 📄 LinkedIn CV Generator

Herramienta para generar currículums profesionales optimizados para ofertas de trabajo utilizando datos de LinkedIn y GitHub.

## 📋 Descripción

LinkedIn CV Generator transforma tu perfil de LinkedIn en currículums optimizados para aplicar a trabajos específicos. El sistema extrae tus datos, los enriquece con información de GitHub y los adapta a cada oferta usando IA.

## 🚀 Características

- **Extracción automática de datos de LinkedIn**: Sube tu PDF exportado y extrae nombre, experiencia, habilidades, educación y más.
- **Integración con GitHub**: Conecta tu perfil para destacar proyectos open source.
- **Optimización con IA**: Adapta tu currículum a ofertas específicas usando OpenAI GPT-4o.
- **Templates ATS-friendly**: Currículums compatibles con sistemas de seguimiento de aplicaciones.
- **Interfaz web intuitiva**: Interfaz Streamlit para generar CVs sin complicaciones.

## 📁 Estructura del Proyecto

```
linkedin_cv_generator/
├── data/
│   └── tu_pdf_linkedin.pdf              # Tu PDF exportado de LinkedIn
├── src/
│   ├── data/
│   │   ├── linkedin_pdf_parser.py       # Parser de PDF de LinkedIn
│   │   └── github_extractor.py           # Extractor de datos de GitHub
│   ├── ai/
│   │   ├── job_analyzer.py               # Análisis de job descriptions con IA
│   │   └── resume_generator.py           # Generador de currículums
│   ├── scraper/
│   │   └── linkedin_scraper.py          # Scraper alternativo (fallback)
│   ├── templates/
│   │   └── ats_template.html            # Template HTML ATS-friendly
│   └── ui/
│       └── app.py                       # Interfaz Streamlit
├── assets/
│   ├── parsed_data/
│   │   ├── parsed_linkedin_profile.json  # Datos parseados de LinkedIn
│   │   └── github_profile_data.json      # Datos de GitHub
│   └── templates/
├── cvs_generados/                        # 📁 ¡Aquí se guardan tus CVs!
│   ├── cv_prueba.html
│   └── cv_gerardobenitez_*.html
├── .env                                  # Configuración (credenciales)
├── requirements.txt                      # Dependencias
├── test_setup.py                         # Test de configuración
├── test_integrated.py                    # Test integrado completo
└── README.md                             # Este archivo
```

## 🛠️ Configuración Inicial

### 1. Instalar dependencias

```bash
# Activar entorno virtual
source linkedin_cv_generator/venv/bin/activate

# Instalar dependencias
pip install -r linkedin_cv_generator/requirements.txt
```

### 2. Configurar credenciales

Edita el archivo `.env`:

```env
# GitHub Token (obtenlo en https://github.com/settings/tokens)
GITHUB_TOKEN=

# OpenAI API Key (opcional, para optimización con IA)
OPENAI_API_KEY=sk-

# Entorno
ENV=development
DEBUG=true
```

### 3. Verificar configuración

```bash
cd linkedin_cv_generator
python test_setup.py
```

Deberías ver: `✅ TODAS LAS PRUEBAS PASARON`

## 📖 Guía de Uso

### Opción 1: Interfaz Web (Recomendado)

```bash
# Iniciar la aplicación
cd linkedin_cv_generator
streamlit run src/ui/app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

#### Pasos en la interfaz:

1. **🏠 Inicio**: Lee la guía de uso
2. **📤 Subir LinkedIn PDF**: 
   - Haz clic en "Selecciona tu PDF"
   - Elige tu archivo PDF exportado de LinkedIn
   - Los datos se extraerán automáticamente
   
3. **💼 GitHub Integration** (opcional):
   - Pega tu GitHub Token Personal Access Token
   - Ingresa tu username de GitHub
   - Se conectarán proyectos destacados

4. **📝 Generar CV**:
   - Pega la descripción del trabajo en el campo de texto
   -Selecciona formato (HTML o PDF)
   - Haz clic en "🚀 Generar CV"
   - Descarga el CV generado

5. **📂 Archivos Generados**:
   - Ve todos tus CVs guardados
   - Descarga cualquier versión anterior

### Opción 2: Línea de comandos

#### Extraer datos de LinkedIn PDF:
```bash
python src/data/linkedin_pdf_parser.py
```

#### Extraer datos de GitHub:
```bash
python src/data/github_extractor.py
```

#### Generar CV:
```bash
python src/ai/resume_generator.py
```

#### Test integrado completo:
```bash
python test_integrated.py
```

## 📤 Exportar PDF de LinkedIn

Para obtener tu PDF de LinkedIn:
1. Ve a tu perfil de LinkedIn
2. Haz clic en "Más" (en tu perfil)
3. Selecciona "Guardar/editar perfil"
4. En la parte superior derecha, haz clic en "Más" → "Exportar perfil"
5. Descarga el archivo PDF generado

## 📁 Dónde se guardan los archivos

- **Currículums generados**: `linkedin_cv_generator/cvs_generados/`
- **Datos parseados**: `linkedin_cv_generator/assets/parsed_data/`
- **Logs y debugging**: `linkedin_cv_generator/assets/`

## 🎯 Funcionalidades Detalladas

### Parser de PDF de LinkedIn

Extrae la siguiente información:
- ✅ Nombre completo
- ✅ Headline profesional (con tecnologías)
- ✅ Información de contacto (email, teléfono)
- ✅ Resumen profesional
- ✅ Habilidades técnicas (hasta 20)
- ✅ Experiencia laboral (empresa, cargo, fechas)
- ✅ Educación
- ✅ Idiomas

### Integración con GitHub

Extrae:
- ✅ Repositorios públicos
- ✅ Lenguajes principales
- ✅ Número de seguidores
- ✅ Proyectos destacados
- ✅ Contribuciones recientes

### Análisis con OpenAI (IA)

Cuando configures tu `OPENAI_API_KEY`:
- ✅ Análisis semántico de job descriptions
- ✅ Matching de habilidades (puntaje 0-100)
- ✅ Optimización de contenido para ATS
- ✅ Reescritura de experiencias con keywords
- ✅ Generación de resúmenes adaptados

### Template ATS-Friendly

Características:
- ✅ Compatible con sistemas de seguimiento de aplicaciones
- ✅ Diseño minimalista y profesional
- ✅ Sin elementos que confundan los parsers
- ✅ Formato HTML limpio y exportable a PDF

## 🛠️ Solución de Problemas

### Error al conectar con GitHub
Verifica que tu GitHub Token tenga permisos de `read:user` y `repo`.

### No se extrae información del PDF
Asegúrate de haber exportado correctamente tu perfil de LinkedIn. El PDF debe contener texto seleccionable (no una imagen escaneada).

### Error de OpenAI API
Verifica que tu API key esté activa y con créditos suficientes en https://platform.openai.com.

## 📝 Personalización

### Modificar la plantilla del CV
Edita el archivo `src/ai/resume_generator.py` y modifica la variable `template` con HTML/CSS personalizado.

### Agregar más habilidades técnicas
Modifica la lista `tech_keywords` en `src/data/linkedin_pdf_parser.py` para incluir tecnologías específicas.

## 🧪 Tests

```bash
# Test de configuración básica
python test_setup.py

# Test integrado completo
python test_integrated.py
```

## 📄 Licencia

Este proyecto es de uso personal y educativo.

## 🤝 Contribuciones

Si tienes mejoras, ¡bienvenidas son! Puedes:
1. Mejorar los parsers de LinkedIn/GitHub
2. Optimizar los prompts de OpenAI
3. Agregar nuevos templates de CV
4. Mejorar la interfaz de usuario

---

**¡Genera currículums profesionales en segundos y destaca en tu próxima aplicación de trabajo!** 🚀