from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from recommender.models import Course
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import logging

# Configure logging
logger = logging.getLogger(__name__)

@csrf_exempt
def recommend_courses(request, course_id):
    try:
        # Log the incoming request
        logger.info(f"Received request for course_id: {course_id}")
        
        # Get the target course
        target_course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        logger.error(f"Course with id {course_id} does not exist")
        return JsonResponse({'error': f'Course with id {course_id} does not exist'}, status=404)

    # Get all courses
    courses = Course.objects.all()
    
    # Log the number of courses
    logger.info(f"Total number of courses: {courses.count()}")

    # Create a list of descriptions, ensuring no empty descriptions
    descriptions = [course.description for course in courses if course.description.strip()]
    
    # Log the number of valid descriptions
    logger.info(f"Number of valid descriptions: {len(descriptions)}")

    if not descriptions:
        logger.error("No valid descriptions found")
        return JsonResponse({'error': 'No valid descriptions found'}, status=400)

    # Compute TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(descriptions)

    # Compute cosine similarity matrix
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    try:
        # Get the index of the target course
        target_index = list(courses).index(target_course)
    except ValueError:
        logger.error("Target course not found in the course list")
        return JsonResponse({'error': 'Target course not found in the course list'}, status=400)

    # Get similarity scores for the target course
    sim_scores = list(enumerate(cosine_sim[target_index]))

    # Sort courses by similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the indices of the most similar courses
    sim_indices = [i[0] for i in sim_scores[1:6]]  # Exclude the target course itself
    
    # Log the indices of the similar courses
    logger.info(f"Indices of similar courses: {sim_indices}")

    # Get the most similar courses
    recommendations = [courses[i] for i in sim_indices]
    
    # Log the titles of the recommended courses
    recommended_titles = [course.title for course in recommendations]
    logger.info(f"Recommended course titles: {recommended_titles}")

    # Prepare the response data
    data = [{
        'title': course.title,
        'description': course.description,
        'university': course.university,
        'location': course.location
    } for course in recommendations]

    return JsonResponse(data, safe=False)
