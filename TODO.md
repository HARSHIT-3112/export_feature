# TODO: Enhance Export Feature for Blogging Site

## Steps to Complete
- [ ] Update `app/proto/export.proto` to add new fields: `author`, `publish_date`, `tags` to `ExportRequest`.
- [ ] Regenerate gRPC stubs (`export_pb2.py` and `export_pb2_grpc.py`) after proto changes.
- [ ] Update `app/services/export_service.py` to handle new fields and pass to exporter functions.
- [ ] Modify `app/utils/file_exporter.py` to incorporate author, publish_date, and tags into PDF/DOCX output (e.g., cover page or footer).
- [ ] Adjust `app/http/export_router.py` to accept and map the new fields from HTTP JSON payload.
- [ ] Test the updated service with sample blog post payloads.
- [ ] Verify exports include new metadata correctly.
