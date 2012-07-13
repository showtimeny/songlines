from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from polls.models import Poll, Choice
from django.shortcuts import render_to_response, get_object_or_404

from reportlab.pdfgen import canvas

def some_view(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=somefilename.pdf'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
       selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
       return render_to_response('polls/detail.html', {
           'poll': p,
           'error_message': "You did not select a choice.",
       }, context_instance=RequestContext(request))
    else:
       selected_choice.votes += 1
       selected_choice.save()
       return HttpResponseRedirect(reverse('poll_results', args=(p.id,)))
