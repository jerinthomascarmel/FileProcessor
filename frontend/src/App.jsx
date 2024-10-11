import "./App.css";
import CustomNavBar from "./components/CustomNavBar";
import HeroSection from "./components/home_page/HeroSection";
import LoginSection from "./components/login_page/LoginSection";
import ErrorSection from "./components/ErrorSection";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import AuthProvider from "react-auth-kit";
import RequireAuth from "@auth-kit/react-router/RequireAuth";
import createStore from "react-auth-kit/createStore";

import { useEffect } from "react";
import Particles from "particlesjs";
function App() {
  useEffect(() => {
    window.onload = function () {
      Particles.init({
        selector: ".background",
        connectParticles: true,
        color: "#d0d3d4",
      });
    };
  }, []);
  const store = createStore({
    authName: "_auth",
    authType: "cookie",
    cookieDomain: window.location.hostname,
    cookieSecure: window.location.protocol === "https:",
  });
  return (
    <>
      <AuthProvider store={store}>
        <BrowserRouter>
          <CustomNavBar />
          <Routes>
            <Route path="/" element={<HeroSection />} />
            <Route
              path={"/"}
              element={
                <RequireAuth fallbackPath={"/login"}>
                  <HeroSection />
                </RequireAuth>
              }
            />

            <Route path="/login" element={<LoginSection />} />
            <Route path="/*" element={<ErrorSection />} />
          </Routes>
          <canvas className="background" style={{ zIndex: "-1" }}></canvas>
        </BrowserRouter>
      </AuthProvider>
    </>
  );
}

export default App;
