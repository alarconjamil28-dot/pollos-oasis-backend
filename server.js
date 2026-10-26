const express = require('express');
const cors = require('cors');
const path = require('path');
const { Pool } = require('pg');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Servir archivos estáticos (index.html)
app.use(express.static(path.join(__dirname)));

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false }
});

// Servir la interfaz web visual en la raíz
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const result = await pool.query('SELECT NOW()');
    res.json({
      status: 'ok',
      message: 'API de Pollos Oasis activa y conectada a Supabase',
      time: result.rows[0].now
    });
  } catch (err) {
    res.status(500).json({ status: 'error', error: err.message });
  }
});

// 1. ENDPOINTS USUARIOS
app.get('/api/users', async (req, res) => {
  try {
    const result = await pool.query('SELECT id, nombre, email, rol, created_at FROM users');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 2. ENDPOINTS PRODUCTOS
app.get('/api/products', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM products ORDER BY id ASC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/products', async (req, res) => {
  const { nombre, precio_compra, precio_venta, stock_actual, stock_minimo } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO products (nombre, precio_compra, precio_venta, stock_actual, stock_minimo) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [nombre, precio_compra, precio_venta, stock_actual || 0, stock_minimo || 5]
    );
    res.status(201).json(result.rows[0]);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 3. ENDPOINTS COMPRAS
app.get('/api/purchases', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM purchases ORDER BY fecha DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 4. ENDPOINTS VENTAS
app.get('/api/sales', async (req, res) => {
  try {
    const result = await pool.query('SELECT * FROM sales ORDER BY fecha DESC');
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// 5. ENDPOINTS KARDEX / MOVIMIENTOS
app.get('/api/inventory-movements', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT im.*, p.nombre as producto_nombre 
      FROM inventory_movements im
      JOIN products p ON im.product_id = p.id
      ORDER BY im.fecha DESC
    `);
    res.json(result.rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(port, () => {
  console.log(`Servidor activo en puerto ${port}`);
});
