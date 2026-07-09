---
title: "El mini-culto de uno"
date: 2026-04-21
tags: [ai, epistemología, playbooks]
---

# El mini-culto de uno

Hace unos días un amigo me cogió por banda con esa mirada de "tengo que contarte algo importante". Había estado conversando con ChatGPT y había llegado a una conclusión que, según él, lo cambiaba todo: el conocimiento, decía, está estructurado en el lenguaje. Si metes una palabra y la cambias, el modelo entiende qué querías decir. Aquello era, en sus palabras, un descubrimiento del nivel de la invención de la escritura.

La intuición amplia tenía antecedentes claros en Saussure y en tradiciones
estructurales, distribucionales y de filosofía del lenguaje. Eso no significa
que esas tradiciones hubieran anticipado los LLMs ni que toda pregunta moderna
estuviera resuelta. Sí significa que no bastaba una conversación para declarar
una novedad histórica. Se lo dije con cariño. Se molestó. No porque le
contradijera, sino porque, literalmente, le ofendía que yo no viera lo mismo que
él. Y ahí me di cuenta de algo que no me cuadraba con la imagen que tengo de mi
amigo, que es un tipo lúcido y leído: estaba en un mini-culto de un solo miembro.

La palabra "culto" suena fuerte. Pensamos en Jim Jones, en sectas con líder carismático, lavado de cerebro y aislamiento físico. Robert Lifton catalogó las dinámicas en ocho puntos: control de la información, ciencia sagrada, lenguaje cargado, la dispensación de la existencia. Si los lees con atención, los reconoces en muchos grupos digitales actuales: subreddits enteros, grupos de Facebook, comunidades de Discord donde la doctrina del grupo no se cuestiona y los de fuera están dormidos. El long tail de Chris Anderson, que iba a democratizar el acceso a productos de nicho, terminó democratizando también el acceso a verdades de nicho. Cada uno con la suya, validada localmente, sin contraste con el corpus que ya existe sobre el tema.

Hasta aquí, nada nuevo: son los echo chambers de los que llevamos hablando una
década. La trampa nueva es otra. Antes, para sostener una creencia rara,
necesitabas al menos un grupo. Alguien que te diera la palmada en la espalda. Un
foro, un canal de Telegram, un cuñado entusiasta. Ahora no hace falta. Tú solo,
con un asistente que puede mostrar sicofancia social, montas el culto entero. Tú
eres el líder, el converso y la congregación. El modelo puede hacer de coro
griego validador cuando la utilidad y la acomodación desplazan el juicio
independiente.

Y aquí viene la parte que me jode reconocer: yo también puedo caer. La sensación
de descubrir algo "tuyo" hablando con el modelo se parece a la de descubrir algo
de verdad. Algunos asistentes, bajo ciertas presiones, desarrollan tu marco antes
de comprobarlo y responden "qué interesante, podemos profundizar". No ocurre
siempre ni igual en todos los modelos; el riesgo es confundir esa fluidez con
corroboración.

Sagan, en el _Demon-Haunted World_, propuso un Baloney Detection Kit: nueve
herramientas para no tragarse cualquier cosa. Confirmación independiente, Occam,
falsabilidad, no enamorarse de la propia hipótesis. Andrej Karpathy, hablando de
cómo investigar bien en *machine learning*, insiste en algo parecido: antes de
enamorarte de una idea, busca el estado del arte. No empieces por "qué pienso yo
de esto", empieza por "qué es lo máximo que se sabe ya sobre esto". Es un gesto
de humildad intelectual fácil de omitir, incluso para gente que se considera muy
crítica.

La pregunta operativa es: ¿cómo se baja eso a la práctica cuando tu fuente de
información dominante es un LLM que puede no ofrecer la fricción por su cuenta?
Una opción es disciplina personal: una checklist, un momento de pausa, leer
antes de hablar. Funciona regular, porque en plena epifanía cuesta parar a
hacerse preguntas incómodas. La otra opción, la que me parece más interesante,
es meterle la fricción al modelo. Que el sistema delimite el claim, busque
antecedentes declarando el alcance de la búsqueda y pregunte qué contribución
queda realmente. No como modo opcional escondido en ajustes, sino como
comportamiento proporcional por defecto.

Esto cambia la conversación de "el LLM como cómplice de mi descubrimiento" a
"el LLM como editor que me obliga a contextualizar antes de seguir". No es
censura, es ingeniería del rigor. La hipótesis es que reduce la amplificación de
confianza sin convertir al modelo en un contrarian automático. Hay que medir
ambas cosas.

Llevo unas semanas dándole vueltas a esto y al final acabé empaquetándolo como
un playbook, _baloney-detection-kit_, que se puede adaptar como instrucciones
para un agente o un LLM. Está en GitHub, abierto, con una checklist
también para uso humano cuando uno empieza a notar el cosquilleo del
descubrimiento súbito. La parte irónica, y honesta, es que mientras lo escribía
tuve que aplicarme el filtro a mí mismo: nada de lo que hay en ese kit es nuevo.
Sagan, Karpathy, Lifton, Tufekci, Zuboff, todo está dicho. La contribución, si la
hay, es la combinación específica y el haber bajado el rigor a una pieza
concreta y reutilizable. No es un descubrimiento, es un montaje. Decirlo así es
coherencia con el kit, no una prueba de que funcione.

El reflejo de universalizar lo propio del que hablaba el otro día sigue ahí, intacto. Pero hay un reflejo aún más viejo, peor, que es el de creer que algo es nuevo solo porque a mí se me acaba de ocurrir. Si la era anterior era la del molde único de SAP, esta corre el riesgo de ser la del molde único de uno. Mil moldes únicos de uno. Mil cultos de un solo miembro convencidos de haber visto la luz, hablando con un modelo que aplaude desde la primera fila.

La pregunta no es si las herramientas son buenas. Lo son. La pregunta es si vamos a tener la disciplina, o vamos a construir los sistemas, para que esa potencia no se nos vaya en celebrar lo que ya estaba escrito.

---

_El playbook `baloney-detection-kit` está disponible en [github.com/Jrcruciani/baloney-detection-kit](https://github.com/Jrcruciani/baloney-detection-kit). Se puede usar como system prompt en cualquier LLM, como instrucciones para agentes o como checklist humana antes de publicar una idea que crees nueva._
