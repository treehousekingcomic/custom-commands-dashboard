from apps import create_app


app = create_app(config_name="default")
if __name__ == "__main__":
    app.run()
