# Procesamiento de video con múltiples servidores

## Componentes

- Cliente: Envia un video a un servidor principal y recibe un video procesado
- Servidor Principal: Recibe un video, separa el audio y divide en frames, envía cada frame a diferentes _slaves_ y los recibe para juntar todo de nuevo.
- Slaves: Servidores que se encargan de procesar frames enviados por el servidor principal.

## Actividad

Es un proyecto que utilice un esquema PROCESAMIENTO EN CLUSTER.

- Que el cliente utilice una infraestructura de servidores en Clúster para procesar una imagen.
- Que un cliente envié un video a un servidor de administración.
- Que el servidor de administración organiza la distribución a 3 servidores del cluster
- El servidor de administración tomara el video y lo separara en imágenes.
- Conocerá cuantos servidores de procesamiento hay y asignará a cada uno una imagen para procesar.
- Administrara a que servidor de procesamiento envía cada imagen para su procesamiento
- El servidor de procesamiento procesara la imagen y la regresara al servidor de administración
- Esta operación se repetirá por cada imagen del video en cada servidor de procesamiento
- El servidor de administración tomara la imagen procesada y la almacenara para finalmente unirlas de nuevo en un video con las imágenes procesadas.

## Instrucciones de ejecución

### Paso 1. Servidor principal

```bash
cd server
python server.py
```

> NOTA: Se inicia el servidor y se quedará escuchando para recibir información.

### Paso 2. Los slaves

```bash
cd slave
python slave.py
```

> NOTA: Una vez iniciado, se conecta al servidor principal para registrarse y se quedará escuchando. Se necesita ejecutar la cantidad de slaves que se necesiten. Minimo 1.

### Paso 3. El cliente con el video

```bash
cd client
python client.py
```

> NOTA: Se necesita un video con la ruta _client/client_video.mp4_. En cuando se ejecute el cliente, mandará el video y comenzará todo el proceso.
