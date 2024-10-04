import Lottie from "lottie-react";
import UserAnimation from "../../assets/login_animation.json";
import LoginForm from "./LoginForm";

function LoginSection() {
  return (
    <div className="container p-5 mt-5">
      <div className="row">
        <div className="col-lg-7 col-12">
          <Lottie animationData={UserAnimation} style={{ height: "25rem" }} />
        </div>
        <div className="col-lg-5 col-12 mt-5">
          <LoginForm />
        </div>
      </div>
    </div>
  );
}

export default LoginSection;
