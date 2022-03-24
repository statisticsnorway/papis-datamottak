from .sas7bdat import SAS7BDAT
import logging
import os
import shutil
import tempfile


class PseudoSas7bdat (SAS7BDAT):
    def __init__(self, path, algorithm, log_level=logging.INFO,
                 extra_time_format_strings=None,
                 extra_date_time_format_strings=None,
                 extra_date_format_strings=None,
                 skip_header=False,
                 encoding='utf8',
                 encoding_errors='ignore',
                 align_correction=True,
                 fh=None, strip_whitespace_from_strings=False):
        
        if (not fh) and (not os.path.isfile(path)):
            raise FileNotFoundError('File not found')
        fh = fh or open(path, 'rb')

        super().__init__(path, log_level, 
                                 extra_time_format_strings,
                                 extra_date_time_format_strings,
                                 extra_date_format_strings,
                                 skip_header, encoding,
                                 encoding_errors, align_correction,
                                 fh, strip_whitespace_from_strings)
        self.algorithm = algorithm
        if len(self.columns) == 0:
            self.logger.waring('no columns found')
        if self.properties.compression:
            self.logger.error(
                        'cannot use %s compression', 
                        self.properties.compression
                    )


        self.filename = path
        
    @classmethod
    def copyFile(cls, fsrc, fdst):
        fsrc.seek(0)
        fdst.seek(0)
        shutil.copyfileobj(fsrc, fdst)
        fsrc.seek(0)
        fdst.seek(0)
    
    def listColumns(self):
        li = list()
        for col in self.columns:
            li.append([col.col_id, col.name, col.label, col.format,
                       col.type, col.length])
        return li
    
    def checkColomnNames(self, columnNames): #True if 
        for col in columnNames:
            if not col in self.column_names:
                return False
        return True
    
    def pseudo(self, pseudoColumns,
                 encrypt=True,
                 suffix='tmp',
                 tempDir = tempfile.gettempdir(),
                 delete = True):
        if self.properties.compression:
            raise IOError('Compression not supported')
        
        for col in pseudoColumns:
            if not col in self.column_names:
                raise ValueError('pseudonym not found')
                
        self.encrypt = encrypt
        self.tempFile = tempfile.NamedTemporaryFile(suffix=suffix, 
                                                    dir = tempDir, 
                                                    delete = delete)
        self.copyFile(self._file, self.tempFile)
        self._pseudoLines(pseudoColumns, encrypt)
        return self.tempFile
        
    def _pseudoLines(self, pseudoColumns, encrypt):
        
        bit_offset = self.header.PAGE_BIT_OFFSET
        subheader_pointer_length = self.header.SUBHEADER_POINTER_LENGTH
        row_count = self.header.properties.row_count
        current_row_in_file_index = 0
        current_row_on_page_index = 0
        
        self.cached_page = None
        self._read_next_page2(self.properties.header_length)
        
        while current_row_in_file_index < row_count:
            current_row_in_file_index += 1
            current_page_type = self.current_page_type
            if current_page_type == self.header.PAGE_META_TYPE:
                try:
                    current_subheader_pointer =\
                        self.current_page_data_subheader_pointers[
                            current_row_on_page_index
                        ]
                except IndexError:
                    self._read_next_page2()
                    current_row_on_page_index = 0
                else:
                    current_row_on_page_index += 1
                    cls = self.header.SUBHEADER_INDEX_TO_CLASS.get(
                        self.header.DATA_SUBHEADER_INDEX
                    )
                    if cls is None:
                        raise NotImplementedError
                    cls(self).process_subheader(
                        current_subheader_pointer.offset,
                        current_subheader_pointer.length
                    )
                    if current_row_on_page_index ==\
                            len(self.current_page_data_subheader_pointers):
                        self._read_next_page2()
                        current_row_on_page_index = 0
            elif current_page_type in self.header.PAGE_MIX_TYPE:
                if self.align_correction:
                    align_correction = (
                        bit_offset + self.header.SUBHEADER_POINTERS_OFFSET +
                        self.current_page_subheaders_count *
                        subheader_pointer_length
                    ) % 8
                else:
                    align_correction = 0
                offset = (
                    bit_offset + self.header.SUBHEADER_POINTERS_OFFSET +
                    align_correction + self.current_page_subheaders_count *
                    subheader_pointer_length + current_row_on_page_index *
                    self.properties.row_length
                )
                try:
                    self.current_row = self._process_byte_array_with_data2(
                        offset,
                        self.properties.row_length,
                        pseudoColumns
                    )
                except:
                    self.logger.exception(
                        'failed to process data (you might want to try '
                        'passing align_correction=%s to the SAS7BDAT '
                        'constructor)' % (not self.align_correction)
                    )
                    raise
                current_row_on_page_index += 1
                if current_row_on_page_index == min(
                    self.properties.row_count,
                    self.properties.mix_page_row_count
                ):
                    self._read_next_page2()
                    current_row_on_page_index = 0
            elif current_page_type == self.header.PAGE_DATA_TYPE:
                self.current_row = self._process_byte_array_with_data2(
                    bit_offset + self.header.SUBHEADER_POINTERS_OFFSET +
                    current_row_on_page_index *
                    self.properties.row_length,
                    self.properties.row_length, pseudoColumns
                )
                current_row_on_page_index += 1
                if current_row_on_page_index == self.current_page_block_count:
                    self._read_next_page2()
                    current_row_on_page_index = 0
            else:
                self.logger.error('unknown page type: %s', current_page_type)
            #yield self.current_row
        if isinstance(self.cached_page, Cached_page):
            self.cached_page.flush(self.tempFile)

    def _read_next_page2(self, start=None):
        self.current_page_data_subheader_pointers = []
        self.cached_page = self._read_cache(self.properties.page_length, start)
        if len(self.cached_page.cache) <= 0:
            self.cached_page = b''
            return

        if len(self.cached_page.cache) != self.properties.page_length:
            self.logger.error(
                'failed to read complete page from file (read %s of %s bytes)',
                len(self.cached_page.cache), self.properties.page_length
            )
        self.header.read_page_header()
        if self.current_page_type == self.header.PAGE_META_TYPE:
            self.header.process_page_metadata()
        if self.current_page_type not in [
            self.header.PAGE_META_TYPE,
            self.header.PAGE_DATA_TYPE
        ] + self.header.PAGE_MIX_TYPE:
            self._read_next_page2()

    def _read_bytes(self, offsets_to_lengths):
        result = {}
        if not self.cached_page:
            for offset, length in offsets_to_lengths.items():
                skipped = 0
                while skipped < (offset - self.current_file_position):
                    seek = offset - self.current_file_position - skipped
                    skipped += seek
                    self._file.seek(seek, 0)
                tmp = self._file.read(length)
                if len(tmp) < length:
                    self.logger.error(
                        'failed to read %s bytes from sas7bdat file', length
                    )
                self.current_file_position = offset + length
                result[offset] = tmp
        else:
            if isinstance(self.cached_page, Cached_page):
                cached_page = self.cached_page.cache
            else:
                cached_page = self.cached_page
            for offset, length in offsets_to_lengths.items():
                result[offset] = cached_page[offset:offset + length]
        return result
    
    def _process_byte_array_with_data2(self, offset, 
                                      length, 
                                      pseudoColumns):
        row_elements = []
        if self.properties.compression and length < self.properties.row_length:
            decompressor = self.DECOMPRESSORS.get(
                self.properties.compression
            )
            source = decompressor(self).decompress_row(
                offset, length, self.properties.row_length,
                self.cached_page.cache
            )
            offset = 0
            raise IOError('Unsupported compression')
        else:
            source = self.cached_page.cache
        for i in range(self.properties.column_count):
            length = self.column_data_lengths[i]
            if length == 0:
                continue
            start = offset + self.column_data_offsets[i]
            end = offset + self.column_data_offsets[i] + length
            temp = source[start:end]
##############
            if not self.columns[i].name in pseudoColumns:
                continue

            readval = self._read_val('s', temp, length)
            decode = readval.decode(self.encoding, self.encoding_errors)
            if self.encrypt:
                decode = self.algorithm.encrypt(decode)
            else:
                decode = self.algorithm.decrypt(decode)
            decode = bytearray(decode.encode(self.encoding, self.encoding_errors))
            source[start:end] = decode
            self.cached_page.modified = True
            #row_elements.append(decode)
            #row_elements.append(temp)
            #row_elements.append(len(decode))
            #row_elements.append(len(temp))
            
            #return row_elements
##############         
            if self.columns[i].type == 'number':
                if self.column_data_lengths[i] <= 2:
                    row_elements.append(self._read_val(
                        'h', temp, length
                    ))
                else:
                    fmt = self.columns[i].format
                    if not fmt:
                        row_elements.append(self._read_val(
                            'number', temp, length
                        ))
                    elif fmt in self.TIME_FORMAT_STRINGS:
                        row_elements.append(self._read_val(
                            'time', temp, length
                        ))
                    elif fmt in self.DATE_TIME_FORMAT_STRINGS:
                        row_elements.append(self._read_val(
                            'datetime', temp, length
                        ))
                    elif fmt in self.DATE_FORMAT_STRINGS:
                        row_elements.append(self._read_val(
                            'date', temp, length
                        ))
                    else:
                        row_elements.append(self._read_val(
                            'number', temp, length
                        ))
            else:  # string
                row_elements.append(self._read_val(
                    's', temp, length
                ).decode(self.encoding, self.encoding_errors))
        return row_elements

 
    
    def _read_cache(self, page_length, start=None):
        if start != None:
            self._file.seek(start)
            self.cached_page = None
        if getattr(self.cached_page, 'modified', None):
            self.tempFile.seek(self.cached_page.start)
            self.tempFile.write(self.cached_page.cache)
        
        start = self._file.tell()
        cache = self._file.read(page_length)
        end = self._file.tell()
        return Cached_page(cache, start, end)
  
class Cached_page():
    def __init__(self, cache, start, end):
        self.cache = bytearray(cache)
        self.start = start
        self.end = end
        self.modified = False

    def flush(self, fh):
        fh.seek(self.start)
        fh.write(self.cache)
        
        