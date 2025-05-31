# Spinventory

**Spinventory** es una aplicación web avanzada para la gestión de colecciones de discos de vinilo y música, desarrollada con Flask, Jinja2 y Sirope/Redis. Su objetivo es ofrecer una experiencia intuitiva, robusta y visualmente atractiva para los amantes de la música y el coleccionismo.

---

## Funcionalidades principales

- **Gestión de Colección Personal:**  
  Añade, edita y elimina discos de tu colección con facilidad. Cada disco puede incluir título, artista, año, género, estado de conservación y una portada visual.

- **WishList:**  
  Lleva un registro de los discos que deseas conseguir, con la misma facilidad y detalle que tu colección principal.

- **Sistema de Usuarios:**  
  Registro y autenticación segura mediante Flask-Login. Cada usuario tiene su propio espacio y puede explorar las colecciones de otros miembros de la comunidad.

- **Reseñas y Valoraciones Compartidas:**  
  Los usuarios pueden dejar una única reseña por disco (por título y artista), compartiendo así las valoraciones y opiniones entre todos los ejemplares iguales, sin importar quién los posea. Las valoraciones se muestran de forma visual con un sistema de estrellas interactivo y animado.

- **Imágenes Inteligentes:**  
  Al subir o descargar una portada, el sistema calcula automáticamente un hash único de la imagen. Si la imagen ya existe, se reutiliza, evitando duplicados y ahorrando espacio en el servidor. Así, aunque varios usuarios añadan el mismo álbum, la imagen solo se almacena una vez.

- **Generación automática de portadas mediante API:**  
  Si el usuario lo desea, puede obtener la portada de un disco automáticamente gracias a la integración con una API externa. Esto facilita y agiliza el proceso de añadir discos a la colección, mejorando la experiencia de usuario.

- **Interfaz Moderna y Responsive:**  
  El diseño es limpio, atractivo y adaptado a dispositivos móviles. El menú superior incluye el logo centrado, navegación clara y el nombre de usuario destacado en un recuadro elegante.

- **Notificaciones y Mensajes:**  
  El sistema informa al usuario de cada acción relevante (añadir, editar, borrar, errores, etc.) de forma clara y no intrusiva.

- **Integridad y Robustez:**  
  La aplicación gestiona los errores de forma elegante, informando al usuario y evitando caídas inesperadas. Los datos se almacenan de forma fiable en Redis mediante Sirope.

- **Gestión de Relaciones:**  
  Las reseñas están asociadas a discos por título y artista, permitiendo compartir opiniones entre usuarios. Si un disco es eliminado, la aplicación está preparada para manejar correctamente las reseñas asociadas.

- **Favicon y Personalización Visual:**  
  La web cuenta con un favicon personalizado y un logo profesional, reforzando la identidad visual del proyecto.

---

## Detalles técnicos y buenas prácticas

- **Modularidad:**  
  El código está organizado en módulos por entidad, facilitando el mantenimiento y la escalabilidad.

- **Front-end personalizado:**  
  Uso de CSS propio para una experiencia visual moderna, con animaciones y componentes interactivos.

- **Navegación fluida:**  
  El menú permite moverse por toda la aplicación sin necesidad de usar el botón “atrás” del navegador.

- **Almacenamiento eficiente:**  
  Gracias al sistema de imágenes únicas y la gestión de relaciones, se optimiza el uso de recursos y se mantiene la integridad de los datos.

---

## Instalación y ejecución

1. Clona el repositorio.
2. Instala las dependencias con `pip install -r requirements.txt`.
3. Configura Redis y las variables necesarias en `config.py`.
4. Ejecuta la aplicación con:
   ```
   flask run --host=0.0.0.0
   ```
5. Accede a la web desde tu navegador.

---

Spinventory es mucho más que un simple inventario: es una comunidad y una herramienta inteligente para disfrutar, compartir y descubrir música de una forma moderna y eficiente.