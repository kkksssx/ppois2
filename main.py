from controller import AppController

if __name__ == "__main__":
    try:
        app = AppController()
        app.run()
    except Exception as e:
        print(f" Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()