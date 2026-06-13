import { useState } from "react";
import API from "../api/axios";
import { useNavigate, Link } from "react-router-dom";
export default function Register() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("/auth/register", form);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      navigate("/dashboard");
    } catch { setError("Registration failed. Email may already exist."); }
  };
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center text-blue-600 mb-6">AI Project Manager</h1>
        {error && <p className="text-red-500 mb-4">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input className="w-full border p-2 rounded" type="text" placeholder="Full Name"
            value={form.full_name} onChange={e => setForm({...form, full_name: e.target.value})} required />
          <input className="w-full border p-2 rounded" type="email" placeholder="Email"
            value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
          <input className="w-full border p-2 rounded" type="password" placeholder="Password"
            value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
          <button className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700" type="submit">Register</button>
        </form>
        <p className="text-center mt-4">Have account? <Link to="/login" className="text-blue-600">Login</Link></p>
      </div>
    </div>
  );
}
