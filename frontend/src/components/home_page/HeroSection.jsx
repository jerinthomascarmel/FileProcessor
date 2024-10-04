import Lottie from "lottie-react";
import FileUploadAnimation from "../../assets/file_upload_image.json";
import FormBox from "./FormBox";

function HeroSection() {
  return (
    <div className="container p-5 mt-5">
      <div className="row">
        <div className="col-lg-5 col-12">
          <Lottie
            animationData={FileUploadAnimation}
            style={{ height: "25rem" }}
          />
        </div>
        <div className="col-lg-1 d-none d-lg-block"></div>
        <div className="col-lg-6 col-12 mt-3">
          <FormBox />
        </div>
      </div>
    </div>
  );
}

export default HeroSection;
