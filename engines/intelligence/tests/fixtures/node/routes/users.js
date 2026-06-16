const express = require("express");
const router = express.Router();

router.get("/users", (req, res) => {
  res.json([]);
});

router.post("/users", (req, res) => {
  res.status(201).json({});
});

module.exports = router;
