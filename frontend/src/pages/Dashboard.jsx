import { useState, useEffect } from "react";
import API from "../api/axios";
import { useNavigate } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];
export default function Dashboard() {
  const [user, setUser] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [teams, setTeams] = useState([]);
  const [newProject, setNewProject] = useState({ name: "", description: "", team_id: "" });
  const [newTeam, setNewTeam] = useState({ name: "", description: "" });
  const [newTask, setNewTask] = useState({ title: "", description: "", priority: "medium", project_id: "" });
  const [aiDescription, setAiDescription] = useState("");
  const [aiProjectId, setAiProjectId] = useState("");
  const [aiMessage, setAiMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    const u = localStorage.getItem("user");
    if (!u) { navigate("/login"); return; }
    setUser(JSON.parse(u));
    fetchData();
  }, []);
  const fetchData = async () => {
    try {
      const [p, tm] = await Promise.all([API.get("/projects/"), API.get("/teams/")]);
      setProjects(p.data);
      setTeams(tm.data);
    } catch {}
  };
  const fetchTasks = async (projectId) => {
    try { const res = await API.get(`/tasks/project/${projectId}`); setTasks(res.data); } catch {}
  };
  const createTeam = async () => {
    try { await API.post("/teams/", newTeam); setNewTeam({ name: "", description: "" }); fetchData(); } catch {}
  };
  const createProject = async () => {
    if (!newProject.team_id) { alert("Select a team first"); return; }
    try { await API.post("/projects/", newProject); setNewProject({ name: "", description: "", team_id: "" }); fetchData(); } catch {}
  };
  const createTask = async () => {
    if (!newTask.project_id) { alert("Select a project"); return; }
    try { await API.post("/tasks/", newTask); fetchTasks(newTask.project_id); } catch {}
  };
  const updateTaskStatus = async (taskId, status) => {
    try { await API.put(`/tasks/${taskId}`, { status }); setTasks(tasks.map(t => t.id === taskId ? {...t, status} : t)); } catch {}
  };
  const aiBreakdown = async () => {
    if (!aiDescription || !aiProjectId) { alert("Enter description and select project"); return; }
    setLoading(true);
    try {
      const res = await API.post("/ai/breakdown", { project_description: aiDescription, project_id: aiProjectId });
      setAiMessage(res.data.message); fetchTasks(aiProjectId);
    } catch { setAiMessage("AI request failed"); }
    setLoading(false);
  };
  const logout = () => { localStorage.clear(); navigate("/login"); };
  const taskStats = [
    { name: "Todo", value: tasks.filter(t => t.status === "todo").length },
    { name: "In Progress", value: tasks.filter(t => t.status === "in_progress").length },
    { name: "Review", value: tasks.filter(t => t.status === "review").length },
    { name: "Done", value: tasks.filter(t => t.status === "done").length },
  ];
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-blue-600 text-white px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">AI Project Manager</h1>
        <div className="flex items-center gap-4">
          <span>{user?.full_name}</span>
          <button onClick={logout} className="bg-white text-blue-600 px-3 py-1 rounded text-sm">Logout</button>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow text-center">
            <div className="text-3xl font-bold text-blue-600">{teams.length}</div>
            <div className="text-gray-500">Teams</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow text-center">
            <div className="text-3xl font-bold text-green-600">{projects.length}</div>
            <div className="text-gray-500">Projects</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow text-center">
            <div className="text-3xl font-bold text-purple-600">{tasks.length}</div>
            <div className="text-gray-500">Tasks</div>
          </div>
        </div>
        {tasks.length > 0 && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-4 shadow">
              <h3 className="font-semibold mb-2">Task Status</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={taskStats}><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value" fill="#3b82f6"/></BarChart>
              </ResponsiveContainer>
            </div>
            <div className="bg-white rounded-lg p-4 shadow">
              <h3 className="font-semibold mb-2">Distribution</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart><Pie data={taskStats} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {taskStats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]}/>)}
                </Pie><Tooltip/></PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-4 shadow">
            <h2 className="text-lg font-semibold mb-3">Create Team</h2>
            <input className="w-full border p-2 rounded mb-2" placeholder="Team name" value={newTeam.name} onChange={e => setNewTeam({...newTeam, name: e.target.value})}/>
            <input className="w-full border p-2 rounded mb-2" placeholder="Description" value={newTeam.description} onChange={e => setNewTeam({...newTeam, description: e.target.value})}/>
            <button onClick={createTeam} className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">Create Team</button>
            <div className="mt-3 space-y-1">{teams.map(t => <div key={t.id} className="text-sm bg-blue-50 p-2 rounded">{t.name}</div>)}</div>
          </div>
          <div className="bg-white rounded-lg p-4 shadow">
            <h2 className="text-lg font-semibold mb-3">Create Project</h2>
            <select className="w-full border p-2 rounded mb-2" value={newProject.team_id} onChange={e => setNewProject({...newProject, team_id: e.target.value})}>
              <option value="">Select Team</option>
              {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
            <input className="w-full border p-2 rounded mb-2" placeholder="Project name" value={newProject.name} onChange={e => setNewProject({...newProject, name: e.target.value})}/>
            <input className="w-full border p-2 rounded mb-2" placeholder="Description" value={newProject.description} onChange={e => setNewProject({...newProject, description: e.target.value})}/>
            <button onClick={createProject} className="w-full bg-green-600 text-white p-2 rounded hover:bg-green-700">Create Project</button>
            <div className="mt-3 space-y-1">{projects.map(p => (
              <div key={p.id} className="text-sm bg-green-50 p-2 rounded cursor-pointer hover:bg-green-100" onClick={() => fetchTasks(p.id)}>
                {p.name} <span className="text-xs text-gray-400">(click to load tasks)</span>
              </div>
            ))}</div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 shadow">
          <h2 className="text-lg font-semibold mb-3">🤖 AI Task Breakdown</h2>
          <select className="w-full border p-2 rounded mb-2" value={aiProjectId} onChange={e => setAiProjectId(e.target.value)}>
            <option value="">Select Project</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <textarea className="w-full border p-2 rounded mb-2" rows={3} placeholder="Describe your project..."
            value={aiDescription} onChange={e => setAiDescription(e.target.value)}/>
          <button onClick={aiBreakdown} disabled={loading} className="w-full bg-purple-600 text-white p-2 rounded hover:bg-purple-700 disabled:opacity-50">
            {loading ? "AI is thinking..." : "Generate Tasks with AI"}
          </button>
          {aiMessage && <p className="text-green-600 mt-2">{aiMessage}</p>}
        </div>
        <div className="bg-white rounded-lg p-4 shadow">
          <h2 className="text-lg font-semibold mb-3">Create Task</h2>
          <div className="grid grid-cols-2 gap-2">
            <select className="border p-2 rounded" value={newTask.project_id} onChange={e => { setNewTask({...newTask, project_id: e.target.value}); fetchTasks(e.target.value); }}>
              <option value="">Select Project</option>
              {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <select className="border p-2 rounded" value={newTask.priority} onChange={e => setNewTask({...newTask, priority: e.target.value})}>
              <option value="low">Low</option><option value="medium">Medium</option>
              <option value="high">High</option><option value="urgent">Urgent</option>
            </select>
            <input className="border p-2 rounded" placeholder="Task title" value={newTask.title} onChange={e => setNewTask({...newTask, title: e.target.value})}/>
            <input className="border p-2 rounded" placeholder="Description" value={newTask.description} onChange={e => setNewTask({...newTask, description: e.target.value})}/>
          </div>
          <button onClick={createTask} className="w-full mt-2 bg-yellow-500 text-white p-2 rounded hover:bg-yellow-600">Create Task</button>
        </div>
        {tasks.length > 0 && (
          <div className="bg-white rounded-lg p-4 shadow">
            <h2 className="text-lg font-semibold mb-3">Task Board</h2>
            <div className="grid grid-cols-4 gap-4">
              {["todo","in_progress","review","done"].map(status => (
                <div key={status} className="bg-gray-50 rounded p-3">
                  <h3 className="font-medium text-sm mb-2 capitalize">{status.replace("_"," ")}</h3>
                  {tasks.filter(t => t.status === status).map(task => (
                    <div key={task.id} className="bg-white border rounded p-2 mb-2 text-sm shadow-sm">
                      <p className="font-medium">{task.title}</p>
                      <p className="text-xs text-gray-400 mb-1">{task.priority}</p>
                      <select className="text-xs border rounded w-full" value={task.status} onChange={e => updateTaskStatus(task.id, e.target.value)}>
                        <option value="todo">Todo</option><option value="in_progress">In Progress</option>
                        <option value="review">Review</option><option value="done">Done</option>
                      </select>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
