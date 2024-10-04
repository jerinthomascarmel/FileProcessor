import axios from "axios";
import { useState } from "react";
import Alert from "react-bootstrap/Alert";
import Lottie from "lottie-react";
import LoadingAnimation from "../../assets/loading.json";
import JSZip from "jszip";

function FormBox() {
  const [wordFile, setWordFile] = useState(null);
  const [excelFile, setExcelFile] = useState(null);
  let [loading, setLoading] = useState(false);
  let [error, setError] = useState({ message: "", type: "nil" });
  let [isValidExcel, setIsValidExcel] = useState(false);
  let [isValidWord, setIsValidWord] = useState(false);
  const [downloadLink, setDownloadLink] = useState(null); // Store the download link
  const apiUrl = import.meta.env.VITE_API_URL;

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!isValidExcel || !isValidWord) {
      setError({
        type: "warning",
        message: "please fill correct file type ",
      });
      return;
    }

    const formData = new FormData();
    formData.append("word_file", wordFile);
    formData.append("excel_file", excelFile);

    setLoading(true); // Set loading to true
    try {
      // Create a new zip instance
      const zip = new JSZip();
      if (wordFile) zip.file("word_file.docx", wordFile);
      if (excelFile) zip.file("excel_file.xlsx", excelFile);

      // Generate the zip file
      const zipFile = await zip.generateAsync({ type: "blob" });

      // Create a new FormData and append the compressed zip file
      const formData = new FormData();
      formData.append("zip_file", zipFile, "files.zip");

      // Send the formData with the zip file to the backend
      const response = await axios.post(`${apiUrl}/upload`, formData, {
        responseType: "blob", // Expecting a blob response (the zip file)
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // Unzip the response file
      const zipBlob = response.data;
      const jsZipInstance = new JSZip();
      const zipContent = await jsZipInstance.loadAsync(zipBlob);

      // Extract the .xlsx file from the zip
      const xlsxFile = await zipContent
        .file("processed_result.xlsx")
        .async("blob");

      // Create a download link for the extracted .xlsx file
      const xlsxUrl = window.URL.createObjectURL(xlsxFile);
      setDownloadLink(xlsxUrl);

      setError({
        type: "success",
        message: "files processed successfully!",
      });
    } catch (error) {
      console.dir(error);
      setError({
        type: "danger",
        message: `Error occurred while uploading files! ${error.message}`,
      });
    } finally {
      setLoading(false); // Set loading to false after request completes
    }
  };

  const handleExcelFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const isValidExcel =
        file.type ===
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" ||
        file.type === "application/vnd.ms-excel";
      setExcelFile(isValidExcel ? file : null);
      setIsValidExcel(isValidExcel); // Set validity based on file type
    } else {
      setExcelFile(null);
      setIsExcelValid(false); // No file selected, set invalid
    }
  };

  const handleWordFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const isValidWord =
        file.type ===
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
        file.type === "application/msword";
      setWordFile(isValidWord ? file : null);
      setIsValidWord(isValidWord); // Set validity based on file type
    } else {
      setWordFile(null);
      setIsValidWord(false); // No file selected, set invalid
    }
  };

  return (
    <form
      className="container needs-validation border p-5 rounded  border-secondary-subtle"
      onSubmit={handleSubmit}
    >
      <h3>Process Files Now!</h3>
      <div className="mb-3">
        <label htmlFor="formFile" className="form-label">
          Upload Excel File
        </label>
        <input
          className="form-control border border-black"
          type="file"
          id="formFile"
          accept=".xlsx"
          onChange={handleExcelFileChange}
          required
        />
      </div>
      <div className="mb-3">
        <label htmlFor="formFile" className="form-label">
          Upload Word File
        </label>
        <input
          className="form-control border border-black"
          type="file"
          id="formFile"
          accept=".doc,.docx"
          onChange={handleWordFileChange}
          required
        />
      </div>

      <div className="row">
        <div className="col-8 ">
          {loading && (
            <div className="row">
              <div className="col-3 mt-2">Loading...</div>
              <div className="col-4">
                <Lottie
                  animationData={LoadingAnimation}
                  style={{ height: "2.5rem", width: "2.5rem" }}
                />
              </div>
            </div>
          )}
          {!loading && error.type == "danger" && (
            <Alert variant="danger">{error.message}</Alert>
          )}
          {!loading && error.type == "success" && (
            <Alert variant="success">{error.message}</Alert>
          )}
          {!loading && error.type == "warning" && (
            <Alert variant="warning">{error.message}</Alert>
          )}
        </div>
        <div className="col-4">
          <button
            type="submit"
            className="btn btn-primary"
            style={{ backgroundColor: "#a074f4", width: "100%" }}
            disabled={loading}
          >
            {loading ? "Processing.." : "Start Processing"}
          </button>
        </div>
      </div>

      {/* Conditionally render the download link */}
      {!loading && downloadLink && (
        <p>
          <a
            href={downloadLink}
            className="link-success link-offset-2 link-underline-opacity-25 link-underline-opacity-100-hover"
            download="processed_result.xlsx"
          >
            Click here to download the processed file
          </a>
        </p>
      )}
    </form>
  );
}

export default FormBox;
