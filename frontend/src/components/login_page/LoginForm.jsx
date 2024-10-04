import Alert from "react-bootstrap/Alert";
import { useState } from "react";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import axios from "axios";
import { useNavigate } from "react-router-dom"; // Import useNavigate

function LoginForm() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const signIn = useSignIn();
  const navigate = useNavigate();
  const apiUrl = import.meta.env.VITE_API_URL;

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent the default form submission
    if (!username || !password) {
      setError("fill the username and password first! ");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${apiUrl}/login`, {
        username,
        password,
      });

      setError(null);
      console.dir(response.data);
      if (
        signIn({
          auth: {
            token: response.data.token,
            type: "Bearer",
          },
          expiresIn: 3600,
          userState: { username },
        })
      ) {
        // Redirect or do-something
        navigate("/");
      } else {
        setError("can't signin! ");
      }
    } catch (err) {
      setError(err.message); // Set error message
    } finally {
      setLoading(false); // Set loading to false after request completes
    }
  };
  return (
    <div className="container">
      <h3>Login now</h3>
      <form onSubmit={handleSubmit}>
        <div className="mb-1">
          <label htmlFor="username" className="form-label">
            Username
          </label>
          <input
            type="username"
            className="form-control"
            id="username"
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="mb-1">
          <label htmlFor="password" className="form-label">
            Password
          </label>
          <input
            type="password"
            className="form-control"
            id="password"
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button
          className="btn pl-2 pr-2 fs-5 text-white mt-2 mb-2"
          style={{
            width: "40%",
            margin: "0 auto",
            backgroundColor: "#a074f4",
          }}
          disabled={loading}
        >
          {loading ? "loading..." : "Login"}
        </button>
        {error && <Alert variant="danger">{error}</Alert>}
      </form>
    </div>
  );
}

export default LoginForm;
