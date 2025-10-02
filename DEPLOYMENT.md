# DigitalOcean Deployment Guide

## Prerequisites
- DigitalOcean account
- GitHub repository with your code
- Docker installed locally (for testing)

## Files Created for Deployment

### 1. `Dockerfile`
- Containerizes the Streamlit application
- Uses Python 3.11-slim base image
- Exposes port 8501 for Streamlit
- Includes health check endpoint

### 2. `docker-compose.yml`
- For local development and testing
- Maps port 8501 to host
- Sets environment variables

### 3. `.dockerignore`
- Optimizes Docker build by excluding unnecessary files
- Reduces image size and build time

### 4. `.do/app.yaml`
- DigitalOcean App Platform configuration
- Specifies Python environment and runtime commands
- Sets required environment variables

## Deployment Steps

### Option 1: DigitalOcean App Platform (Recommended)

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Add DigitalOcean deployment configuration"
   git push origin main
   ```

2. **Create App on DigitalOcean**:
   - Go to DigitalOcean App Platform
   - Click "Create App"
   - Connect your GitHub repository
   - Select the branch (main/master)

3. **Configure App**:
   - DigitalOcean will auto-detect the configuration from `.do/app.yaml`
   - Review the settings:
     - Name: `abstract-renumber-tool`
     - Environment: Python
     - Build Command: Auto-detected
     - Run Command: `streamlit run streamlit_main.py --server.port=8080 --server.address=0.0.0.0`

4. **Environment Variables** (automatically set from app.yaml):
   - `PDF_BACKEND=pypdf`
   - `STREAMLIT_SERVER_PORT=8080`
   - `STREAMLIT_SERVER_ADDRESS=0.0.0.0`

5. **Deploy**:
   - Click "Create Resources"
   - Wait for deployment to complete
   - Access your app via the provided URL

### Option 2: DigitalOcean Droplet with Docker

1. **Create Droplet**:
   - Choose Ubuntu 22.04 LTS
   - Minimum 2GB RAM (4GB recommended for large files)
   - Enable monitoring

2. **Setup Docker**:
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker $USER
   ```

3. **Deploy Application**:
   ```bash
   git clone https://github.com/your-username/aa-abstract-renumber.git
   cd aa-abstract-renumber
   docker-compose up -d
   ```

4. **Configure Firewall**:
   ```bash
   sudo ufw allow 8501
   sudo ufw enable
   ```

## Local Testing

Test the Docker build locally before deployment:

```bash
# Build the image
docker build -t streamlit-app .

# Run the container
docker run -p 8501:8501 streamlit-app

# Or use docker-compose
docker-compose up
```

Access the app at `http://localhost:8501`

## Configuration Notes

### File Upload Limits
- Your app handles large files (400MB limit mentioned in README)
- Ensure sufficient memory allocation:
  - App Platform: Use at least `basic-xs` instance size
  - Droplet: Minimum 4GB RAM recommended

### Environment Variables
The following environment variables are configured:
- `PDF_BACKEND=pypdf`: Specifies PDF processing backend
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server
- `STREAMLIT_SERVER_ADDRESS`: Server address binding

### Health Checks
- Docker health check: `/_stcore/health`
- App Platform will automatically monitor this endpoint

## Troubleshooting

### Build Issues
- Check Docker build logs: `docker build -t streamlit-app . --no-cache`
- Verify all dependencies in requirements.txt

### Runtime Issues
- Check container logs: `docker logs <container_id>`
- Verify environment variables are set correctly
- Ensure file permissions for uploads

### Memory Issues
- Monitor memory usage in DigitalOcean dashboard
- Consider upgrading instance size for large file processing
- Implement file size validation in Streamlit app

## Security Considerations

- App Platform provides HTTPS automatically
- Consider adding authentication for production use
- Validate file uploads thoroughly
- Monitor resource usage and costs

## Cost Optimization

- Start with `basic-xxs` instance ($5/month)
- Scale up based on usage patterns
- Monitor bandwidth usage for large file uploads/downloads
- Consider implementing file cleanup routines

## Next Steps

1. Update the GitHub repository URL in `.do/app.yaml`
2. Push code to GitHub
3. Deploy via DigitalOcean App Platform
4. Test the deployed application
5. Configure custom domain (optional)
6. Set up monitoring and alerts
