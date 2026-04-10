// Simple filter by search and location
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("jobSearch");
    const locationFilter = document.getElementById("locationFilter");
    const jobsContainer = document.getElementById("jobsContainer");

    if (searchInput && locationFilter) {
        searchInput.addEventListener("input", filterJobs);
        locationFilter.addEventListener("change", filterJobs);
    }

    function filterJobs() {
        const searchValue = searchInput.value.toLowerCase();
        const locationValue = locationFilter.value.toLowerCase();

        const jobCards = jobsContainer.querySelectorAll(".job-card");

        jobCards.forEach(card => {
            const title = card.querySelector(".card-title").textContent.toLowerCase();
            const location = card.querySelector(".card-text:nth-child(3)").textContent.toLowerCase();
            if (title.includes(searchValue) && (location.includes(locationValue) || !locationValue)) {
                card.parentElement.style.display = "block";
            } else {
                card.parentElement.style.display = "none";
            }
        });
    }
});
function applyJob(jobId){

let confirmApply = confirm("Do you want to apply for this job?");

if(confirmApply){

alert("You have successfully applied for the job!");

}

}
function hireWorker(workerId){

let confirmHire = confirm("Do you want to hire this worker?");

if(confirmHire){

alert("Worker hired successfully!");

}

}
