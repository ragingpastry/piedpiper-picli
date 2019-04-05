from charon.cloudutils import base

class Openstack(base.Base):
    
    def __init__(self, config):
        super(Openstack, self).__init__(config)

    
    def __enter__(self):
        self.launch_instance()

    def __exit__(self, *args):
        self.destroy_instance()

    def generate_onetime_key(self):
        """
        One-Time SSH deployment key
        """
        pass

    def launch_instance(self):
        """
        Start an instance
        """
        print "Hello there"
    
    def get_instance_status(self):
        """
        Get status of an instance 
        """
        pass
    
    def get_instance_ip(self):
        """
        Get instance  
        """
        pass

    def destroy_instance(self):
        """
        Remove an instance
        """
        print "General kenobi"

    def validate_image(self):
        """
        Validate that an image exists
        """
        pass