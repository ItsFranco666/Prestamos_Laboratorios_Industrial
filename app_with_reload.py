import sys
import time
import subprocess
import os
import traceback
import logging
from datetime import datetime
from watchdog.observers import Observer # type: ignore
from watchdog.events import FileSystemEventHandler # type: ignore
import threading

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None
        self.restart_app()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Solo recargar si se modifican archivos .py
        if event.src_path.endswith('.py'):
            print(f"🔄 Cambio detectado en: {os.path.basename(event.src_path)}")
            time.sleep(0.5)  # Pequeña pausa para asegurar que el archivo se ha guardado completamente
            self.restart_app()
    
    def _stream_output(self, stream, prefix=""):
        try:
            for line in iter(stream.readline, ''):
                if line:
                    print(f"{prefix}{line}", end='')
        except Exception as e:
            print(f"❌ Error leyendo salida del proceso: {e}")

    def restart_app(self):
        # Terminar el proceso anterior si existe
        if self.process and self.process.poll() is None:
            print("🛑 Cerrando aplicación anterior...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        
        print("🚀 Iniciando aplicación...")
        print("📝 Logs se guardarán en app_debug.log")
        print("-" * 50)
        
        # Iniciar nuevo proceso
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            # Lanzar hilos para mostrar stdout y stderr en tiempo real
            self.stdout_thread = threading.Thread(target=self._stream_output, args=(self.process.stdout, ""), daemon=True)
            self.stderr_thread = threading.Thread(target=self._stream_output, args=(self.process.stderr, "[ERR] "), daemon=True)
            self.stdout_thread.start()
            self.stderr_thread.start()
        except Exception as e:
            print(f"❌ Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    # Configurar logging
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            logging.FileHandler('app_debug.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    script_path = "main.py"
    
    print("🔍 Monitor de Recarga Automática")
    print("=" * 60)
    
    # Verificar que el archivo principal existe
    if not os.path.exists(script_path):
        print(f"❌ Error: No se encontró {script_path}")
        sys.exit(1)
    
    try:
        logging.info(f"📁 Directorio monitoreado: {os.getcwd()}")
        logging.info(f"🐍 Script principal: {script_path}")
        logging.info("🤖 Monitoreando cambios en archivos Python...")
        logging.info("💡 Presiona Ctrl+C para detener el monitor")
        
        # Crear el manejador de eventos y el observador
        event_handler = ReloadHandler(script_path)
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n")
        print("🛑 Deteniendo monitor...")
        observer.stop()
        
        # Terminar el proceso de la aplicación si está corriendo
        if event_handler.process and event_handler.process.poll() is None:
            print("🛑 Cerrando aplicación...")
            event_handler.process.terminate()
            try:
                event_handler.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                event_handler.process.kill()
                event_handler.process.wait()
        
        print("✅ Monitor detenido correctamente")
    except Exception as e:
        logging.error("❌ Error crítico en la aplicación:")
        logging.error(f"Error: {str(e)}")
        logging.error("Traceback completo:")
        logging.error(traceback.format_exc())
        print(f"❌ Error crítico en la aplicación: {e}")
    finally:
        observer.join()
