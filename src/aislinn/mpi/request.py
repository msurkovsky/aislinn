#
#    Copyright (C) 2014 Stanislav Bohm
#
#    This file is part of Aislinn.
#
#    Aislinn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 of the License, or
#    (at your option) any later version.
#
#    Aislinn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Kaira.  If not, see <http://www.gnu.org/licenses/>.
#


from base.utils import EqMixin


class Request(EqMixin):

    def is_send(self):
        return False

    def is_receive(self):
        return False

    def is_completed(self):
        return False


class SendRequest(Request):

    Standard = 0
    Synchronous = 1

    def __init__(self, message, send_type):
        assert send_type == self.Standard or send_type == self.Synchronous
        self.message = message
        self.send_type = send_type

    def is_standard_send(self):
        return self.send_type == SendRequest.Standard

    def is_send(self):
        return True

    def compute_hash(self, hashthread):
        hashthread.update("SR {0}".format(self.send_type))
        self.message.compute_hash(hashthread)

    def __repr__(self):
        return "<SendRequest {0}>".format(self.send_type)


class ReceiveRequest(Request):

    def __init__(self, source, tag, data_ptr, size):
        self.source = source
        self.tag = tag
        self.data_ptr = data_ptr
        self.size = size

    def is_receive(self):
        return True

    def compute_hash(self, hashthread):
        hashthread.update(
                "RR {0.source} {0.tag} {0.data_ptr} {0.size} ".format(self))

    def __repr__(self):
        return "RECV(source={0.source}, tag={0.tag})".format(self)


class CompletedRequest(Request):

    def __init__(self, original_request):
        self.original_request = original_request

    def compute_hash(self, hashthread):
        hashthread.update("CR ")

    def is_completed(self):
        return True
