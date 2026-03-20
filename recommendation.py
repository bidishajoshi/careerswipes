from ai_matcher import ai_match

def get_filtered_recommendations(user, all_jobs, threshold=30.0):
    recommended = []
    
    for job in all_jobs:
        # Compare user's interested_job title with the actual job title
        score = ai_match(user.interested_job, job.title)
        
        # Only include if it meets a certain similarity percentage
        if score >= threshold:
            recommended.append(job)
            
    return recommended