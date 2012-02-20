import boto


class CounterPool(object):
    '''
    Handles schema level interactions with DynamoDB and generates individual
    counters as needed.
    '''
    table_name = None
    schema = {
        'hash_key_name': 'counter_name',
        'hash_key_proto_value': 'S',
    }
    read_units = 3
    write_units = 5

    def __init__(self, aws_access_key=None, aws_secret_key=None, table_name=None, schema=None, read_units=None, write_units=None, auto_create_table=True, ):
        """
        :aws_access_key:
            AWS Acccess Key ID with permissions to use DynamoDB
        :aws_secret_key:
            AWS Access Secret Key for the given Access Key ID
        :table_name:
            The DynamoDB table that should be used to store this pool's
            counters.  See http://bit.ly/DynamoDBModel for details on
            DynamoDB's data model.
        :schema:
            The schema that will be used to create a table if one does not
            already exist.  See the `boto`<http://bit.ly/BotoCreateTable>_
            docs for details on what's expected for a schema.
        :read_units:
            Read throughput to be set when a table is created.  See
            http://bit.ly/DynamoThoughput for details on Dynamo's provisioned
            throughput system.
        :write_units:
            Write throughput to be set when a table is created.
        :auto_create_table:
            Should Albertson create a dynamodb table if the provided
            `table_name` doesn't exist.
        """
        self.conn = self.get_conn(aws_access_key, aws_secret_key)
        self.table_name = table_name or self.table_name
        self.schema = schema or self.schema
        self.read_units = read_units or self.read_units
        self.write_units = write_units or self.write_units
        self.auto_create_table = auto_create_table

        super(CounterPool, self).__init__()

    def get_conn(self, aws_access_key=None, aws_secret_key=None):
        '''
        Hook point for overriding how the CounterPool gets its connection to
        AWS.
        '''
        return boto.connect_dynamodb(
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

    def get_table_name(self):
        '''
        Hook point for overriding how the CounterPool determines the table name
        to use.
        '''
        if not self.table_name:
            raise NotImplementedError(
                'You must provide a table_name value or override the get_table_name method'
            )
        return self.table_name

    def get_schema(self):
        '''
        Hook point for overriding how the CounterPool determines the schema
        to be used when creating a missing table.
        '''
        if not self.schema:
            raise NotImplementedError(
                'You must provide a schema value or override the get_schema method'
            )

        return self.conn.create_schema(**self.schema)

    def get_read_units(self):
        '''
        Hook point for overriding how the CounterPool determines the read
        throughput units to set on a newly created table.
        '''
        return self.read_units

    def get_write_units(self):
        '''
        Hook point for overriding how the CounterPool determines the write
        throughput units to set on a newly created table.
        '''
        return self.write_units

    def create_table(self):
        '''
        Hook point for overriding how the CounterPool creates a new table
        in DynamooDB
        '''
        return self.conn.create_table(
            name=self.get_table_name(),
            schema=self.get_schema(),
            read_units=self.get_read_units(),
            write_units=self.get_write_units(),
        )

    def get_table(self):
        '''
        Hook point for overriding how the CounterPool transforms table_name
        into a boto DynamoDB Table object.
        '''
        try:
            table = self.conn.get_table(self.get_table_name())
        except boto.exception.DynamoDBResponseError:
            if self.auto_create_table:
                table = self.create_table()
            else:
                raise

        return table
