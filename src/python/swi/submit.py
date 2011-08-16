# Copyright (c) 2010 Derek Murray <derek.murray@cl.cam.ac.uk>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
from ciel.runtime.exceptions import ErrorReferenceError

'''
Created on 15 Apr 2010

@author: dgm36
'''
from ciel.runtime.object_cache import retrieve_object_for_ref
import ciel.runtime.util.start_job
import time
import datetime
import sys
import os
from optparse import OptionParser

def now_as_timestamp():
    return (lambda t: (time.mktime(t.timetuple()) + t.microsecond / 1e6))(datetime.datetime.now())

def main():
    parser = OptionParser()
    parser.add_option("-m", "--master", action="store", dest="master", help="Master URI", metavar="MASTER", default=os.getenv("CIEL_MASTER"))
    parser.add_option("-i", "--id", action="store", dest="id", help="Job ID", metavar="ID", default="default")
    parser.add_option("-e", "--env", action="store_true", dest="send_env", help="Set this flag to send the current environment with the script as _env", default=False)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", help="Set this flag to enable verbose output", default=False)
    parser.add_option("-p", "--package-file", action="append", type="string", dest="package_files", help="Specify files to be included as package inputs", metavar="KEY FILENAME", nargs=2, default=[])
    (options, args) = parser.parse_args()
   
    if not options.master:
        parser.print_help()
        print >> sys.stderr, "Must specify master URI with --master"
        sys.exit(1)

    if len(args) != 1:
        parser.print_help()
        print >> sys.stderr, "Must specify one script file to execute, as argument"
        sys.exit(1)

    script_name = args[0]
    master_uri = options.master
    id = options.id
    
    if options.verbose:
        print id, "STARTED", now_as_timestamp()

    swi_package = {"swimain": {"filename": script_name}}

    for key, filename in options.package_files:
        swi_package[key] = {"filename": filename}
    
    swi_args = {"sw_file_ref": {"__package__": "swimain"}, "start_args": args}
    if options.send_env:
        swi_args["start_env"] = dict(os.environ)
    else:
        swi_args["start_env"] = {}

    new_job = ciel.runtime.util.start_job.submit_job_with_package(swi_package, "swi", swi_args, {}, os.getcwd(), master_uri, args)
    
    result = ciel.runtime.util.start_job.await_job(new_job["job_id"], master_uri)
    
    try:
        reflist = retrieve_object_for_ref(result, "json", None)
        sw_return = retrieve_object_for_ref(reflist[0], "json", None)
    except ErrorReferenceError, ere:
        print >>sys.stderr, 'Task failed with an error'
        print >>sys.stderr, '%s: "%s"' % (ere.ref.reason, ere.ref.details)
        sys.exit(-2)
    
    return sw_return
    
if __name__ == '__main__':
    main()
