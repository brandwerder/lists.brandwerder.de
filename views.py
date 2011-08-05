# -*- coding: utf-8 -*-
# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import re
from mailman.client import Client
from forms import *
from settings import API_USER, API_PASS
import sys #Error handing info
from urllib2 import HTTPError

@login_required
def domain_index(request, template = 'mailman-django/domain_index.html'):
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        existing_domains = c.domains
    except AttributeError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                 {'error': "REST API not found / Offline"},
				 context_instance=RequestContext(request))
    return render_to_response(template, {'domains':existing_domains,},
					          context_instance=RequestContext(request))  

@login_required
def domain_new(request, template = 'mailman-django/domain_new.html'):
    message = None
    if request.method == 'POST':
        form = DomainNew(request.POST)
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
            if form.is_valid():
                mail_host = form.cleaned_data['mail_host']
                web_host = form.cleaned_data['web_host']
                description = form.cleaned_data['description']
                try:
                    domain = c.create_domain(mail_host,web_host,description)
                except HTTPError, e:
                    message=e
                return redirect("domain_index")
        except AttributeError, e:
            return render_to_response('mailman-django/errors/generic.html', 
                                      {'error': "REST API not found / Offline", 
                                      'is_ajax':is_ajax},
                                      context_instance=RequestContext(request))
    else:
        form = DomainNew()
    return render_to_response(template, {'form': form,'message':message},   
                              context_instance=RequestContext(request))        

@login_required
def administration(request): #TODO
    """
    Administration dashboard used for Menu navigation
    """
    
    return render_to_response('mailman-django/errors/generic.html', 
                                  {'message':  "This Site is in preperation."})#TODO

@login_required
def list_new(request, template = 'mailman-django/lists/new.html'):
    """
    Add a new mailing list. 
    If the request to the function is a GET request an empty form for 
    creating a new list will be displayed. If the request method is 
    POST the form will be evaluated. If the form is considered
    correct the list gets created and otherwise the form with the data
    filled in before the last POST request is returned. The user must
    be logged in to create a new list.
    """
    error=None
    message=None
    mailing_list=None
    if request.method == 'POST':
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except AttributeError, e:
            return render_to_response('mailman-django/errors/generic.html', 
                                      {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
        choosable_domains = [("",_("Choose a Domain"))]
        for domain in c.domains:
            choosable_domains.append((domain.email_host,domain.email_host))
        form = ListNew(choosable_domains,request.POST)

        if form.is_valid():
            #grab domain
            domain = c.get_domain(form.cleaned_data['mail_host'])
            #creating the list
            try:
                mailing_list = domain.create_list(form.cleaned_data['listname'])
                settings = mailing_list.settings
                settings["description"] = form.cleaned_data['description']
                settings["owner_address"] = form.cleaned_data['list_owner'] #TODO: Readonly
                settings["advertised"] = form.cleaned_data['advertised']
                #settings["???"] = form.cleaned_data['languages'] #TODO not found in REST
                settings.save()
                return redirect("list_summary",fqdn_listname=mailing_list.fqdn_listname)
            except HTTPError, e: #TODO catch correct Error class
                return render_to_response('mailman-django/errors/generic.html', 
                                      {'error':e},
                                      context_instance=RequestContext(request))
    else:
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        except AttributeError, e:
            return render_to_response('mailman-django/errors/generic.html', 
                                      {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
        choosable_domains = [("",_("Choose a Domain"))]
        for domain in c.domains:
            choosable_domains.append((domain.email_host,domain.email_host))
        form = ListNew(choosable_domains)
    return render_to_response(template, {'form': form, error:None}, context_instance=RequestContext(request))


def list_index(request, template = 'mailman-django/lists/index.html'):
    """Show a table of all mailing lists.
    """
    error=None
    if request.method == 'POST':
        return redirect("list_summary", fqdn_listname=request.POST["list"])
    else:
        return render_to_response(template, {'error':error},context_instance=RequestContext(request)) #lists by context processor


def list_summary(request,fqdn_listname=None,option=None,template='mailman-django/lists/summary.html'):
    """
    PUBLIC
    an entry page for each lists which allows some simple tasks per LIST
    """
    error=None
    user_is_subscribed = False
    if request.method == 'POST':
        return redirect("list_summary", fqdn_listname=request.POST["list"])
    else:
        try:
            c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
            the_list = c.get_list(fqdn_listname)
            try:
                the_list.get_member(request.user.username)
                user_is_subscribed = True
            except: pass #init
        except AttributeError, e:
            return render_to_response('mailman-django/errors/generic.html', 
                                      {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
    return render_to_response(template, 
                                  {'list':the_list,
                                   'message':  None,
                                   'user_is_subscribed':user_is_subscribed,
                                  },
                                  context_instance=RequestContext(request)
                                  )

def list_subscriptions(request, option=None, fqdn_listname=None, user_email = None,
                       template = 'mailman-django/lists/subscriptions.html', *args, **kwargs):#TODO **only kwargs ?
    """
    Display the information there is available for a list. This 
    function also enables subscribing or unsubscribing a user to a 
    list. For the latter two different forms are available for the 
    user to fill in which are evaluated in this function.
    """
    #create Values for Template usage   
    message = None
    error = None
    form_subscribe = None
    form_unsubscribe = None
    if request.POST.get('fqdn_listname', ''):
        fqdn_listname = request.POST.get('fqdn_listname', '')
    # connect REST and catch issues getting the list
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except AttributeError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
    except HTTPError,e :
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': _("List ")+fqdn_listname+_(" does not exist")},context_instance=RequestContext(request))
    #process submitted form    
    if request.method == 'POST':
        form = False
        # The form enables both subscribe and unsubscribe. As a result
        # we must find out which was the case.
        if request.POST.get('name', '') == "subscribe":
            form = ListSubscribe(request.POST)
            if form.is_valid():
                # the form was valid so try to subscribe the user
                try:
                    email = form.cleaned_data['email']
                    response = the_list.subscribe(address=email,real_name=form.cleaned_data.get('real_name', ''))
                    return render_to_response('mailman-django/lists/summary.html', 
                                              {'list': the_list,
                                               'option':option,
                                               'message':_("Subscribed ")+ email },context_instance=RequestContext(request))
                except HTTPError, e:
                    return render_to_response('mailman-django/errors/generic.html', 
                                      {'error':e}, context_instance=RequestContext(request))
            else: #invalid subscribe form
                form_subscribe = form
                form_unsubscribe = ListUnsubscribe(initial = {'fqdn_listname': fqdn_listname, 'name' : 'unsubscribe'})       
        elif request.POST.get('name', '') == "unsubscribe":
            form = ListUnsubscribe(request.POST)
            if form.is_valid():
                #the form was valid so try to unsubscribe the user
                try:
                    response = the_list.unsubscribe(address=form.cleaned_data["email"])
                    return render_to_response('mailman-django/lists/summary.html', 
                                              {'list': the_list, 'message':_("Unsubscribed ")+ email },context_instance=RequestContext(request))
                except ValueError, e:
                    return render_to_response('mailman-django/errors/generic.html', 
                                      {'error':e}, context_instance=RequestContext(request))   
            else:#invalid unsubscribe form
                form_subscribe = ListSubscribe(initial = {'fqdn_listname': fqdn_listname,
                                                               'option':option,
                                                               'name' : 'subscribe'})
                form_unsubscribe = ListUnsubscribe(request.POST)
    else:
        # the request was a GET request so set the two forms to empty
        # forms
        if option=="subscribe" or not option:
            form_subscribe = ListSubscribe(initial = {'fqdn_listname': fqdn_listname, 'email':request.user.username, 
                                             'name' : 'subscribe'})
        if option=="unsubscribe" or not option:                                             
            form_unsubscribe = ListUnsubscribe(initial = {'fqdn_listname': fqdn_listname, 'email':request.user.username, 
                                                 'name' : 'unsubscribe'})
    the_list = c.get_list(fqdn_listname)#TODO
    return render_to_response(template, {'form_subscribe': form_subscribe,
                                         'form_unsubscribe': form_unsubscribe,
                                         'message':message,
                                         'error':error,
                                         'list': the_list,
                                         }
                                         ,context_instance=RequestContext(request))

@login_required
def list_delete(request, fqdn_listname = None, 
                template = 'mailman-django/lists/index.html'):
    """
    Delete a list by providing the full list name including domain.
    """
    # create a connection to Mailman and get the list
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
        if request.method == 'POST':
            the_list.delete()
            # let the user return to the list index page
            lists = c.lists
            return redirect("list_index")
        else:
            submit_url = reverse('list_delete',kwargs={'fqdn_listname':fqdn_listname})
            cancel_url = reverse('list_index',)
            return render_to_response('mailman-django/confirm_dialog.html',
                        {'submit_url': submit_url,
                         'cancel_url': cancel_url,
                        'list':the_list,},
                        context_instance=RequestContext(request))
    except AttributeError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
    except HTTPError,e :
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': _("List ")+fqdn_listname+_(" does not exist")},context_instance=RequestContext(request))

@login_required
def list_settings(request, fqdn_listname = None, visible_section=None, visible_option=None,
                  template = 'mailman-django/lists/settings.html'):
    """
    View and edit the settings of a list.
    The function requires the user to be logged in and have the 
    permissions necessary to perform the action.
    
    Use /<NAMEOFTHESECTION>/<NAMEOFTHEOPTION>
    to show only parts of the settings
    <param> is optional / is used to differ in between section and option might result in using //option
    """
    message = ""
    
    #Create the Connection
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except AttributeError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
    except HTTPError,e :
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': _("List ")+fqdn_listname+_(" does not exist")},context_instance=RequestContext(request))
    #Save a Form Processed by POST  
    if request.method == 'POST':
        form = ListSettings(visible_section,visible_option,data=request.POST)
        form.truncate()
        if form.is_valid():
            settings = the_list.settings
            for key in form.fields.keys():
                settings[key] = form.cleaned_data[key]
                settings.save()    
            message = _("The list has been updated.")
        else:
            message = _("Validation Error - The list has not been updated.")
    
    else:#Provide a form with existing values
        #create form and process layout into form.layout
        form = ListSettings(visible_section,visible_option,data=None)
        #create a Dict of all settings which are used in the form
        used_settings={}
        for section in form.layout:
            for option in section[1:]:
                used_settings[option] = the_list.settings[option]
        #recreate the form using the settings
        form = ListSettings(visible_section,visible_option,data=used_settings)
        form.truncate()
    if visible_option:
        selected = visible_option
    elif visible_section:
        selected = visible_section
    else:
        selected = None
        
    return render_to_response(template, {'form': form,
                                         'message': message,
                                         'list': the_list,
                                         'selected':selected,
                                         'visible_option':visible_option,
                                         'visible_section':visible_section,
                                         }
                                         ,context_instance=RequestContext(request))

@login_required
def mass_subscribe(request, fqdn_listname = None, 
                   template = 'mailman-django/lists/mass_subscribe.html'):
    """
    Mass subscribe users to a list.
    This functions is part of the settings for a list and requires the
    user to be logged in to perform the action.
    """
    message = ""
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        the_list = c.get_list(fqdn_listname)
    except AttributeError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': "REST API not found / Offline"},context_instance=RequestContext(request))
    except HTTPError,e :
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': _("List ")+fqdn_listname+_(" does not exist")},context_instance=RequestContext(request))
    if request.method == 'POST':
        form = ListMassSubscription(request.POST)
        if form.is_valid():
            try:
                # The emails to subscribe should each be provided on a
                # separate line so get each of them.
                emails = request.POST["emails"].splitlines()
                for email in emails:
                    # very simple test if email address is valid
                    parts = email.split('@')
                    if len(parts) == 2 and '.' in parts[1]: #TODO - move check to clean method of the form - see example in django docs
                        try:
                            the_list.subscribe(address=email, real_name="")
                            message = "The mass subscription was successful."
                        except Exception, e: #TODO find right exception and catch only this one
                            return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': str(e)})

                    else:
                        # At least one email address wasn't valid so 
                        # overwrite the success message and ask them to
                        # try again.
                        message = "Please enter valid email addresses."
            except Exception, e:
                return HttpResponse(e)
    else:
        # A request to view the page was send so return the form to
        # mass subscribe users.
        form = ListMassSubscription()
    return render_to_response(template, {'form': form,
                                         'message': message,
                                         'list': the_list}
                                         ,context_instance=RequestContext(request))

@login_required
def user_settings(request, tab = "user",
                  template = 'mailman-django/user_settings.html',
                  fqdn_listname = None,):
    """
    Change the user or the membership settings.
    The user must be logged in to be allowed to change any settings.
    TODO: * add CSS to display tabs ??
          * add missing functionality in REST server and client and 
            change to the correct calls here
    """
    member = request.user.username
    message = ""
    form = None
    the_list=None
    membership_lists = []
    try:
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        if tab == "membership":
            if fqdn_listname:
                the_list = c.get_list(fqdn_listname)
                user_object = the_list.get_member(member)
            else:
                message = ("Using a workaround to replace missing Client functionality → LP:820827")
                #### BEGIN workaround
                for list in c.lists: 
                    try: 
                        list.get_member(member)
                        membership_lists.append(list)    
                    except: # if user is not subscribed to this list
                        pass
                #### END workaround
        else:
           # address_choices for the 'address' field must be a list of 
           # tuples of length 2
           address_choices = [[addr, addr] for addr in user_object.address]
    except AttributeError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': str(e)+"REST API not found / Offline"},context_instance=RequestContext(request))
    except ValueError, e:
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': e},context_instance=RequestContext(request))                                  
    except HTTPError,e :
        return render_to_response('mailman-django/errors/generic.html', 
                                  {'error': _("List ")+fqdn_listname+_(" does not exist")},context_instance=RequestContext(request))
    #-----------------------------------------------------------------
    if request.method == 'POST':
        # The form enables both user and member settings. As a result
        # we must find out which was the case.
        raise Exception("Please fix bug prior submitting the form")
        if tab == "membership":
            form = MembershipSettings(request.POST)
            if form.is_valid():
                member_object = c.get_member(member, request.GET["list"])
                member_object.update(request.POST)
                message = "The membership settings have been updated."
        else:
            # the post request came from the user tab
            # the 'address' field need choices as a tuple of length 2
            addr_choices = [[request.POST["address"], request.POST["address"]]]
            form = UserSettings(addr_choices, request.POST)
            if form.is_valid(): 
                user_object.update(request.POST)
                # to get the full list of addresses we need to 
                # reinstantiate the form with all the addresses
                # TODO: should return the correct settings from the DB,
                # not just the address_choices (add mock data to _User 
                # class and make the call with 'user_object.info')
                form = UserSettings(address_choices)
                message = "The user settings have been updated."

    else:
        if tab == "membership" and fqdn_listname :
            if fqdn_listname:
                #TODO : fix LP:821069 in mailman.client
                the_list = c.get_list(fqdn_listname)
                member_object = the_list.get_member(member)
                # TODO: add delivery_mode and deliver_status from a 
                # list of tuples at one point, currently we hard code
                # them in forms.py
                # instantiate the form with the correct member info
                """
                acknowledge_posts
                hide_address
                receive_list_copy
                receive_own_postings
                delivery_mode
                delivery_status
                """
                data = {} #Todo https://bugs.launchpad.net/mailman/+bug/821438
                form = MembershipSettings(data)
        elif tab == "user":
            # TODO: should return the correct settings from the DB,
            # not just the address_choices (add mock data to _User 
            # class and make the call with 'user_object._info') The 'language'
            # field must also be added as a list of tuples with correct
            # values (is currently hard coded in forms.py).
            data ={}#Todo https://bugs.launchpad.net/mailman/+bug/821438
            form = UserSettings(data)

    return render_to_response(template, {'form': form,
                                         'tab': tab,
                                         'list': the_list,
                                         'membership_lists': membership_lists,
                                         'message': message,
                                         'member': member}
                                         ,context_instance=RequestContext(request))

def user_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('user_login')

def user_login(request,template = 'mailman-django/login.html'):
    """
    Let the user logout.
    Some functions requires the user to be logged in to perform the
    actions. After the user is done, logging out is possible to avoid
    others having rights they should not have.
    """
    """try:
        del request.session['member_id']
    except KeyError:
        pass
    return list_index(request)
    """ #used to be old style logout - workaround for local django usage
    
    """
    New Login page used with the RESTBackend, will allow login and logout depending on the current user status.
    """
    from django.contrib.auth import authenticate, login
    error = None
    message = None
    form=None
    if request.POST:
        form = Login(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["user"],
                                password=form.cleaned_data["password"])
            if user is not None:
                if user.is_active:
                    if "next" in request.GET.keys():
                        login(request,user)
                        return redirect(request.GET["next"])        
                    else:
                        return redirect("list_index")
                else:
                    error= _("Your account has been disabled!")
            else:
                error = _("Your username and password were incorrect.")
    else:
        form = Login()
        message = "You are required to login to continue. Please provide a valid email address and a password."
    return render_to_response(template, {'form': form,
                                         'error': error,
                                         'message': message,}
                                         ,context_instance=RequestContext(request))
