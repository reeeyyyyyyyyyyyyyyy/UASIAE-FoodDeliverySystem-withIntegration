# Gunakan image Python yang ringan
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code ke dalam container
COPY . .

# Expose port 4000 (sesuai request lama)
EXPOSE 4000

# Jalankan server uvicorn
# Host 0.0.0.0 agar bisa diakses dari luar container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "4000"]