# Space Adventure 🚀

Un juego de disparos espaciales simple desarrollado con Python y Pygame. Controla una nave espacial verde, dispara a los enemigos y sobrevive el mayor tiempo posible.

## 🎮 Descripción

**Space Adventure** es un juego de supervivencia y disparos donde controlas una nave espacial cuadrada verde. Los enemigos rojos aparecen desde los bordes de la pantalla y te persiguen. Tu objetivo es eliminarlos con balas amarillas mientras evitas las colisiones. ¡Cuanto más tiempo sobrevivas, mayor será tu puntuación!

## ✨ Características

- **Controles simples**: Muévete con WASD o las flechas del teclado, dispara con click izquierdo del mouse
- **IA de enemigos**: Los enemigos aparecen desde bordes aleatorios y persiguen al jugador
- **Mecánica de disparo**: Haz click para disparar balas hacia el cursor del mouse
- **Sistema de puntuación**: Gana 10 puntos por cada enemigo eliminado
- **Game over y reinicio**: Presiona ESPACIO para reiniciar después de game over

## 🎯 Controles

- **WASD** o **Flechas del teclado**: Mover la nave espacial
- **Click izquierdo del mouse**: Disparar balas hacia el cursor
- **ESPACIO**: Reiniciar el juego después de game over
- **ESC** o **Cerrar ventana**: Salir del juego

## 📋 Requisitos

- Python 3.6 o superior
- Pygame 2.0.0 o superior

## 🚀 Instalación

1. Asegúrate de tener Python instalado en tu computadora

2. Instala Pygame:
```bash
pip install pygame
```

O instala desde requirements.txt:
```bash
pip install -r requirements.txt
```

3. Ejecuta el juego:
```bash
python space_adventure.py
```

## 🏗️ Estructura del Proyecto

```
space_adventure/
├── space_adventure.py    # Archivo principal del juego
├── requirements.txt      # Dependencias de Python
└── README.md            # Este archivo
```

## 💻 Estructura del Código

El juego está organizado en tres clases principales:

- **Player**: La nave espacial verde que controlas
- **Enemy**: Enemigos rojos que aparecen y te persiguen
- **Bullet**: Proyectiles amarillos que disparas

El bucle principal del juego maneja:
- Procesamiento de eventos (teclado, mouse, cierre de ventana)
- Actualización del estado del juego (movimiento, colisiones, aparición de enemigos)
- Renderizado (dibujar todos los objetos del juego)

## 🎓 Conceptos de Aprendizaje

Este proyecto demuestra:
- **Programación Orientada a Objetos**: Clases para entidades del juego
- **Bucles de juego**: Bucle principal que corre a 60 FPS
- **Detección de colisiones**: Sistema de colisiones basado en rectángulos
- **Matemáticas vectoriales**: Cálculo de direcciones y distancias
- **Manejo de eventos**: Entrada de teclado y mouse
- **Gestión de estado**: Lógica de game over y reinicio

## 🔧 Cómo Funciona

1. **Inicialización**: Crea el jugador, listas vacías para enemigos y balas
2. **Bucle del juego**: Se ejecuta 60 veces por segundo
   - Procesa la entrada del usuario
   - Actualiza todos los objetos del juego
   - Verifica colisiones
   - Dibuja todo en pantalla
3. **Aparición de enemigos**: Nuevos enemigos aparecen cada 1.5 segundos desde bordes aleatorios
4. **Detección de colisiones**: 
   - Enemigo golpea al jugador → Game Over
   - Bala golpea a enemigo → Ambos destruidos, aumenta la puntuación
5. **Game Over**: Muestra la puntuación final, presiona ESPACIO para reiniciar

## 🎨 Personalización

Puedes modificar fácilmente:
- **Colores**: Cambia los valores RGB en las constantes de color
- **Velocidades**: Ajusta los valores `speed` en las clases Player y Enemy
- **Tasa de aparición**: Cambia `1500` en la lógica de aparición de enemigos
- **Tasa de disparo**: Cambia `200` en el tiempo de espera del disparo
- **Tamaño de ventana**: Modifica las constantes `WIDTH` y `HEIGHT`

## 📝 Licencia

Este proyecto es de código abierto y está disponible para fines educativos.

## 🤝 Contribuciones

¡Siéntete libre de hacer fork de este proyecto y agregar tus propias características! Algunas ideas:
- Agregar efectos de sonido y música
- Crear diferentes tipos de enemigos
- Agregar power-ups
- Implementar un sistema de puntuación alta
- Agregar efectos de partículas

---

¡Disfruta del juego! 🎮
