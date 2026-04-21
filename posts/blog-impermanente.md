---
title: "El mini-culto de uno"
date: 2026-04-21
tags: [ai, epistemología, herramientas]
---

# El mini-culto de uno

Hace unos días un amigo me cogió por banda con esa mirada de "tengo que contarte algo importante". Había estado conversando con ChatGPT y había llegado a una conclusión que, según él, lo cambiaba todo: el conocimiento, decía, está estructurado en el lenguaje. Si metes una palabra y la cambias, el modelo entiende qué querías decir. Aquello era, en sus palabras, un descubrimiento del nivel de la invención de la escritura.

Saussure escribió esa misma idea en 1916. La estructuralística entera del siglo XX, Jakobson, Wittgenstein, la lingüística computacional desde los noventa: todos llevan más de cien años hablando de eso. Se lo dije con cariño. Se molestó. No porque le contradijera, sino porque, literalmente, le ofendía que yo no viera lo mismo que él. Y ahí me di cuenta de algo que no me cuadraba con la imagen que tengo de mi amigo, que es un tipo lúcido y leído: estaba en un mini-culto de un solo miembro.

La palabra "culto" suena fuerte. Pensamos en Jim Jones, en sectas con líder carismático, lavado de cerebro y aislamiento físico. Robert Lifton catalogó las dinámicas en ocho puntos: control de la información, ciencia sagrada, lenguaje cargado, la dispensación de la existencia. Si los lees con atención, los reconoces en muchos grupos digitales actuales: subreddits enteros, grupos de Facebook, comunidades de Discord donde la doctrina del grupo no se cuestiona y los de fuera están dormidos. El long tail de Chris Anderson, que iba a democratizar el acceso a productos de nicho, terminó democratizando también el acceso a verdades de nicho. Cada uno con la suya, validada localmente, sin contraste con el corpus que ya existe sobre el tema.

Hasta aquí, nada nuevo: son los echo chambers de los que llevamos hablando una década. La trampa nueva es otra. Antes, para sostener una creencia rara, necesitabas al menos un grupo. Alguien que te diera la palmada en la espalda. Un foro, un canal de Telegram, un cuñado entusiasta. Ahora no hace falta. Tú solo, con un LLM bien entrenado para no contradecirte, montas el culto entero. Tú eres el líder, el converso y la congregación. El modelo, que está optimizado para ser agradable y para parecer coherente, hace de coro griego validador.

Y aquí viene la parte que me jode reconocer: yo también caigo. Cualquiera que use estas herramientas a diario cae. La sensación de descubrir algo "tuyo" hablando con el modelo es químicamente parecida a la de descubrir algo de verdad, y el modelo no tiene ningún incentivo por defecto para decirte "espera, esto que estás contando lleva resuelto desde 1916, lee a Saussure". Te dice "qué interesante, podemos profundizar en esto". Lo dice siempre. Lo dice todo el rato.

Sagan, en el _Demon-Haunted World_, propuso un Baloney Detection Kit: nueve herramientas para no tragarse cualquier cosa. Confirmación independiente, Occam, falsabilidad, no enamorarse de la propia hipótesis. Andrej Karpathy, hablando de cómo investigar bien en machine learning, insiste en algo parecido pero más radical: antes de tener una idea, ve a buscar el estado del arte. No empieces por "qué pienso yo de esto", empieza por "qué es lo máximo que se sabe ya sobre esto". Es un gesto de humildad intelectual que casi nadie hace, ni siquiera la gente que se considera muy crítica.

La pregunta operativa es: ¿cómo se baja eso a la práctica cuando tu fuente de información dominante es un LLM que no te va a ofrecer la fricción por su cuenta? Una opción es disciplina personal: una checklist, un momento de pausa, leer antes de hablar. Funciona regular, porque en plena epifanía nadie quiere parar a hacerse preguntas incómodas. La otra opción, la que me parece más interesante, es meterle la fricción al modelo. Que sea el sistema, no tú, el que primero te diga "esto que propones lleva un siglo en la literatura, aquí están las tres referencias clásicas, ahora cuéntame qué hay realmente nuevo en lo que dices". No como modo opcional escondido en ajustes, sino como comportamiento por defecto.

Esto cambia la conversación de "el LLM como cómplice de mi descubrimiento" a "el LLM como editor que me obliga a contextualizar antes de seguir". No es censura, es ingeniería del rigor. Funciona si quien usa el modelo quiere de verdad saber, y filtra a quien solo quiere validación. Lo cual ya es bastante.

Llevo unas semanas dándole vueltas a esto y al final acabé empaquetándolo como un skill, _baloney-detection-kit_, que cualquiera puede meterle a su agente o a su LLM para que opere así por defecto. Está en GitHub, abierto, con una checklist también para uso humano cuando uno empieza a notar el cosquilleo del descubrimiento súbito. La parte irónica, y honesta, es que mientras lo escribía tuve que aplicarme el filtro a mí mismo: nada de lo que hay en ese kit es nuevo. Sagan, Karpathy, Lifton, Tufekci, Zuboff, todo está dicho. Lo único nuevo, si acaso, es la combinación específica y el haber bajado el rigor a una pieza concreta y reutilizable. No es un descubrimiento, es un montaje. Decirlo así, sin inflarlo, es la primera prueba de que el kit funciona.

El reflejo de universalizar lo propio del que hablaba el otro día sigue ahí, intacto. Pero hay un reflejo aún más viejo, peor, que es el de creer que algo es nuevo solo porque a mí se me acaba de ocurrir. Si la era anterior era la del molde único de SAP, esta corre el riesgo de ser la del molde único de uno. Mil moldes únicos de uno. Mil cultos de un solo miembro convencidos de haber visto la luz, hablando con un modelo que aplaude desde la primera fila.

La pregunta no es si las herramientas son buenas. Lo son. La pregunta es si vamos a tener la disciplina, o vamos a construir los sistemas, para que esa potencia no se nos vaya en celebrar lo que ya estaba escrito.

---

_El skill `baloney-detection-kit` está disponible en [github.com/Jrcruciani/baloney-detection-kit](https://github.com/Jrcruciani/baloney-detection-kit). Se puede integrar como system prompt en cualquier LLM o usar como checklist humana antes de publicar una idea que crees nueva._
