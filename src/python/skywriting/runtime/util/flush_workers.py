# Copyright (c) 2010 Derek Murray <Derek.Murray@cl.cam.ac.uk>
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
from optparse import OptionParser
from skywriting.runtime.util.load import get_worker_netlocs
import httplib2
import os
import sys

def main():
    
    parser = OptionParser()
    parser.add_option("-m", "--master", action="store", dest="master", help="Master URI", metavar="MASTER", default=os.getenv("SW_MASTER"))
    (options, _) = parser.parse_args()

    h = httplib2.Http()

    workers = get_worker_netlocs(options.master)
    
    for netloc in workers:
        response, _ = h.request('http://%s/admin/flush/' % (netloc), 'POST', 'pin')
        assert response.status == 200
        print >>sys.stderr, 'Flushed worker: %s' % netloc
              
if __name__ == '__main__':
    main()