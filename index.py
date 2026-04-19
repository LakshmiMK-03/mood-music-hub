from main import create_app

# Create the flask app instance for Vercel
app = create_app()

# Note: Vercel handles the server execution (app.run is not needed here)
