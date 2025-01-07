
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from .models import RoadmapCourse,RoadmapSlide,RoadmapStage,UserProgress,RoadmapTest,TestQuestion
class RoadmapStageView(View):
    @method_decorator(login_required)
    def get(self, request):
        stages = RoadmapStage.objects.all()
        progress = {stage.id: UserProgress.objects.filter(user=request.user, stage=stage).first() for stage in stages}
        return render(request, 'roadmap/stages.html', {'stages': stages, 'progress': progress})


class RoadmapCourseView(View):
    @method_decorator(login_required)
    def get(self, request, stage_id, course_order):
        stage = get_object_or_404(RoadmapStage, id=stage_id)
        course = get_object_or_404(RoadmapCourse, stage=stage, order=course_order)
        progress, created = UserProgress.objects.get_or_create(user=request.user, stage=stage)
        if progress.current_course != course and not progress.is_stage_completed:
            progress.current_course = course
            progress.save()
        return render(request, 'roadmap/course.html', {'stage': stage, 'course': course})


class RoadmapSlideView(View):
    @method_decorator(login_required)
    def get(self, request, course_id, slide_order):
        course = get_object_or_404(RoadmapCourse, id=course_id)
        slide = get_object_or_404(RoadmapSlide, course=course, order=slide_order)
        slides = course.slides.all()
        next_slide = slides.filter(order__gt=slide.order).first()
        prev_slide = slides.filter(order__lt=slide.order).last()
        return render(request, 'roadmap/slide.html', {'slide': slide, 'next_slide': next_slide, 'prev_slide': prev_slide})

class RoadmapSlideView(View):
    @method_decorator(login_required)
    def get(self, request, course_id, slide_order, *args, **kwargs):
        course = RoadmapCourse.objects.get(id=course_id)
        slide = RoadmapSlide.objects.get(course=course, order=slide_order)
        slides = RoadmapSlide.objects.filter(course=course).order_by("order")
        prev_slide = slides.filter(order__lt=slide_order).last()
        next_slide = slides.filter(order__gt=slide_order).first()
        
        # Check if this is the last course in the stage
        is_last_course = not RoadmapCourse.objects.filter(
            stage=course.stage, order__gt=course.order
        ).exists()

        context = {
            "slide": slide,
            "prev_slide": prev_slide,
            "next_slide": next_slide,
            "is_last_course": is_last_course,
        }
        return render(request, "roadmap/slide.html", context)







from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseForbidden

class RoadmapTestView(View):
    @method_decorator(login_required)
    def get(self, request, stage_id):
        stage = get_object_or_404(RoadmapStage, id=stage_id)
        
        # Check if user has completed all courses in the stage
        user_progress = get_object_or_404(UserProgress, user=request.user, stage=stage)
        last_course = RoadmapCourse.objects.filter(stage=stage).order_by('-order').first()
        
        if not user_progress.current_course or user_progress.current_course.order < last_course.order:
            messages.error(request, "Please complete all courses before taking the test.")
            return redirect('roadmap_stages')

        test = get_object_or_404(RoadmapTest, stage=stage)
        questions = list(TestQuestion.objects.filter(test=test))
        total_questions = len(questions)

        # Get current question number from session or start with first question
        current_question_idx = request.session.get(f'test_{test.id}_current_question', 0)
        
        # Get previously saved answers from session
        saved_answers = request.session.get(f'test_{test.id}_answers', {})
        
        # Get current question
        current_question = questions[current_question_idx]
        
        # Check if this is the first/last question
        is_first_question = current_question_idx == 0
        is_last_question = current_question_idx == total_questions - 1

        # Create options list for template
        options = [
            ('A', current_question.option_a),
            ('B', current_question.option_b),
            ('C', current_question.option_c),
            ('D', current_question.option_d),
        ]
        
        context = {
            'stage': stage,
            'question': current_question,
            'question_number': current_question_idx + 1,
            'total_questions': total_questions,
            'is_first_question': is_first_question,
            'is_last_question': is_last_question,
            'selected_option': saved_answers.get(str(current_question.id)),
            'options': options,  # Add options to context
        }
        
        return render(request, 'roadmap/test_question.html', context)

    @method_decorator(login_required)
    def post(self, request, stage_id):
        stage = get_object_or_404(RoadmapStage, id=stage_id)
        test = get_object_or_404(RoadmapTest, stage=stage)
        questions = list(TestQuestion.objects.filter(test=test))
        total_questions = len(questions)

        # Handle navigation between questions
        if 'next' in request.POST or 'previous' in request.POST:
            # Save current answer
            current_question_idx = request.session.get(f'test_{test.id}_current_question', 0)
            current_question = questions[current_question_idx]
            
            # Get answers dict from session or create new
            saved_answers = request.session.get(f'test_{test.id}_answers', {})
            
            # Save current answer if provided
            selected_option = request.POST.get('selected_option')
            if selected_option:
                saved_answers[str(current_question.id)] = selected_option
                request.session[f'test_{test.id}_answers'] = saved_answers

            # Update current question index
            if 'next' in request.POST and current_question_idx < total_questions - 1:
                request.session[f'test_{test.id}_current_question'] = current_question_idx + 1
            elif 'previous' in request.POST and current_question_idx > 0:
                request.session[f'test_{test.id}_current_question'] = current_question_idx - 1
            
            return redirect('roadmap_test', stage_id=stage_id)

        # Handle test submission
        elif 'submit' in request.POST:
            saved_answers = request.session.get(f'test_{test.id}_answers', {})
            
            # Save the last question's answer if provided
            current_question_idx = request.session.get(f'test_{test.id}_current_question', 0)
            current_question = questions[current_question_idx]
            selected_option = request.POST.get('selected_option')
            if selected_option:
                saved_answers[str(current_question.id)] = selected_option
            
            # Calculate score
            correct_answers = 0
            for question in questions:
                if (saved_answers.get(str(question.id)) == question.correct_option):
                    correct_answers += 1

            score_percentage = (correct_answers / total_questions) * 100

            # Clear test session data
            for key in list(request.session.keys()):
                if key.startswith(f'test_{test.id}'):
                    del request.session[key]

            # Update user progress based on score
            user_progress = get_object_or_404(UserProgress, user=request.user, stage=stage)
            if score_percentage >= test.passing_score:
                user_progress.is_stage_completed = True
                user_progress.badge_earned = True
                user_progress.save()
                
                # Get next stage if exists
                next_stage = RoadmapStage.objects.filter(id__gt=stage.id).first()
                if next_stage:
                    messages.success(request, 
                        f'Congratulations! You passed with {score_percentage:.1f}%. Moving to next stage!')
                    return redirect('roadmap_course', 
                                 stage_id=next_stage.id, 
                                 course_order=1)
                else:
                    messages.success(request, 
                        f'Congratulations! You completed all stages with {score_percentage:.1f}%!')
                    return redirect('roadmap_stages')
            else:
                messages.error(request, 
                    f'You scored {score_percentage:.1f}%. Required: {test.passing_score}%. Please try again.')
                return redirect('roadmap_course', 
                             stage_id=stage.id, 
                             course_order=1)

        return redirect('roadmap_test', stage_id=stage_id)